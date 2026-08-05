from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .lti import is_valid_lti_oauth_signature


@csrf_exempt
def lti_launch_view(request: HttpRequest):
	if request.method != 'POST':
		return HttpResponseBadRequest('LTI launch must be a POST request.')

	launch_params = {k: v for k, v in request.POST.items()}

	if launch_params.get('lti_version') != 'LTI-1p0':
		return HttpResponseBadRequest('Unsupported LTI version.')

	if launch_params.get('lti_message_type') != 'basic-lti-launch-request':
		return HttpResponseBadRequest('Unsupported LTI message type.')

	consumer_key = launch_params.get('oauth_consumer_key', '')
	consumer_secret = settings.LTI_CONSUMERS.get(consumer_key)
	if not consumer_secret:
		return HttpResponseForbidden('Unknown LTI consumer key.')

	if not is_valid_lti_oauth_signature(request, launch_params, consumer_secret):
		return HttpResponseForbidden('Invalid OAuth signature.')

	lti_user_id = launch_params.get('user_id', '').strip()
	email = launch_params.get('lis_person_contact_email_primary', '').strip()
	given_name = launch_params.get('lis_person_name_given', '').strip()
	family_name = launch_params.get('lis_person_name_family', '').strip()
	full_name = launch_params.get('lis_person_name_full', '').strip()

	if email:
		username = f"lti_{email}"
	elif lti_user_id:
		username = f"lti_{lti_user_id}"
	else:
		return HttpResponseBadRequest('Launch payload missing both email and user_id.')

	username = username.lower()[:150]
	user, _ = User.objects.get_or_create(username=username)

	if email:
		user.email = email[:254]
	if given_name:
		user.first_name = given_name[:150]
	if family_name:
		user.last_name = family_name[:150]
	elif full_name and not user.last_name and not user.first_name:
		user.first_name = full_name[:150]

	user.set_unusable_password()
	user.save()

	login(request, user, backend='django.contrib.auth.backends.ModelBackend')
	request.session['lti_launch'] = launch_params

	return redirect('home')


@login_required
def home_view(request: HttpRequest):
	launch_data = request.session.get('lti_launch', {})
	return render(
		request,
		'app/home.html',
		{
			'launch_data': launch_data,
			'user': request.user,
		},
	)

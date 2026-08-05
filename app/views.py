from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .lti import is_valid_lti_oauth_signature
from .models import LtiCourseContext


def _is_instructor_launch(launch_params: dict[str, str]) -> bool:
	roles_value = launch_params.get('roles', '')
	if not roles_value:
		return False

	roles = [role.strip().lower() for role in roles_value.split(',') if role.strip()]
	return any('instructor' in role for role in roles)


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

	if not _is_instructor_launch(launch_params):
		return HttpResponseForbidden('Access denied: only instructors are allowed.')

	moodle_site = (
		launch_params.get('tool_consumer_instance_guid', '').strip()
		or launch_params.get('tool_consumer_instance_url', '').strip()
		or consumer_key.strip()
	)[:255]
	course_id = launch_params.get('context_id', '').strip()[:255]
	course_title = launch_params.get('context_title', '').strip()[:255]

	if moodle_site and course_id:
		LtiCourseContext.objects.update_or_create(
			moodle_site=moodle_site,
			course_id=course_id,
			defaults={'course_title': course_title},
		)

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
	course_contexts = LtiCourseContext.objects.order_by('moodle_site', 'course_title', 'course_id')
	selected_context = None
	selected_context_id = request.GET.get('course_context', '').strip()

	if launch_data:
		moodle_site = (
			launch_data.get('tool_consumer_instance_guid', '').strip()
			or launch_data.get('tool_consumer_instance_url', '').strip()
			or launch_data.get('oauth_consumer_key', '').strip()
		)[:255]
		course_id = launch_data.get('context_id', '').strip()[:255]
		course_title_from_launch = launch_data.get('context_title', '').strip()[:255]

		if moodle_site and course_id:
			selected_context, _ = LtiCourseContext.objects.get_or_create(
				moodle_site=moodle_site,
				course_id=course_id,
				defaults={'course_title': course_title_from_launch},
			)
			if (
				selected_context
				and course_title_from_launch
				and selected_context.course_title != course_title_from_launch
			):
				selected_context.course_title = course_title_from_launch
				selected_context.save(update_fields=['course_title', 'updated_at'])
	elif selected_context_id.isdigit():
		selected_context = course_contexts.filter(id=int(selected_context_id)).first()

	course_title = (
		launch_data.get('context_title')
		or (selected_context.course_title if selected_context and selected_context.course_title else '')
		or 'Course Manager'
	)

	return render(
		request,
		'app/home.html',
		{
			'launch_data': launch_data,
			'course_contexts': course_contexts,
			'selected_context': selected_context,
			'selected_context_id': selected_context_id,
			'user': request.user,
			'course_title': course_title,
		},
	)


@require_http_methods(['GET', 'POST'])
def logout_view(request: HttpRequest):
	logout(request)
	return redirect('login')

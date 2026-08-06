from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .lti import is_valid_lti_oauth_signature
from .models import Course, Question, Site
from .services import handle_question_creation, handle_question_update, handle_question_deletion


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
		site_obj, _ = Site.objects.get_or_create(moodle_site=moodle_site)
		course_obj, created = Course.objects.get_or_create(
			site=site_obj,
			course_id=course_id,
			defaults={'course_title': course_title},
		)
		if not created and course_obj.course_title != course_title:
			course_obj.course_title = course_title
			course_obj.save(update_fields=['course_title', 'updated_at'])

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
    course_contexts = Course.objects.select_related('site').order_by('site__moodle_site', 'course_title', 'course_id')
    questions = Question.objects.select_related('author', 'last_update').order_by('title', 'id')
    selected_context = None
    selected_context_id = request.GET.get('course_context', '').strip()
    modal_error = None

    if launch_data:
        moodle_site = (
            launch_data.get('tool_consumer_instance_guid', '').strip()
            or launch_data.get('tool_consumer_instance_url', '').strip()
            or launch_data.get('oauth_consumer_key', '').strip()
        )[:255]
        course_id = launch_data.get('context_id', '').strip()[:255]
        course_title_from_launch = launch_data.get('context_title', '').strip()[:255]

        school_name = (launch_data.get('custom_school_name', '').strip()[:255] or None)
        if moodle_site and course_id:
            site_obj, _ = Site.objects.get_or_create(moodle_site=moodle_site)
            if school_name and site_obj.custom_moodle_site != school_name:
                site_obj.custom_moodle_site = school_name
                site_obj.save(update_fields=['custom_moodle_site'])
            selected_context, _ = Course.objects.get_or_create(
                site=site_obj,
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

    # Process question submission POST request
    if request.method == 'POST':
        new_question, modal_error = handle_question_creation(request, selected_context)
        if new_question:
            redirect_url = f"{request.path}?question={new_question.id}"
            if selected_context and not launch_data:
                redirect_url += f"&course_context={selected_context.id}"
            return redirect(redirect_url)

    selected_question = None
    selected_question_id = request.GET.get('question', '').strip()

    if selected_question_id.isdigit():
        selected_question = questions.filter(id=int(selected_question_id)).first()
    if selected_question is None:
        selected_question = questions.first()

    if selected_question is not None:
        selected_question = (
            Question.objects
            .select_related('author', 'last_update', 'course')
            .prefetch_related('body', 'files')
            .filter(id=selected_question.id)
            .first()
        )

    course_title = (
        launch_data.get('context_title')
        or (selected_context.course_title if selected_context and selected_context.course_title else '')
        or 'Course Manager'
    )

    site_name = str(selected_context.site) if selected_context else ''

    return render(
        request,
        'app/home.html',
        {
            'launch_data': launch_data,
            'course_contexts': course_contexts,
            'questions': questions,
            'selected_question': selected_question,
            'selected_context': selected_context,
            'selected_context_id': selected_context_id,
            'user': request.user,
            'site_name': site_name,
            'course_title': course_title,
            'modal_error': modal_error,
        },
    )


@require_http_methods(['GET', 'POST'])
def logout_view(request: HttpRequest):
	logout(request)
	return redirect('login')


@login_required
@require_http_methods(['GET', 'POST'])
def question_detail_partial_view(request: HttpRequest, question_id: int):
    selected_question = (
        Question.objects
        .select_related('author', 'last_update', 'course')
        .prefetch_related('body', 'files')
        .filter(id=question_id)
        .first()
    )
    if selected_question is None:
        return JsonResponse({'error': 'Question not found.'}, status=404)

    is_editing = request.GET.get('edit') == 'true'
    edit_error = None

    if request.method == 'POST':
        updated_question, edit_error = handle_question_update(request, selected_question)
        if not edit_error:
            # Turn off edit mode after successful save
            is_editing = False
            # Re-fetch to refresh prefetched related objects (body/files) after mutations.
            selected_question = (
                Question.objects
                .select_related('author', 'last_update', 'course')
                .prefetch_related('body', 'files')
                .filter(id=updated_question.id)
                .first()
            )
        else:
            is_editing = True

    categories = Question.objects.filter(course=selected_question.course).values_list('category', flat=True).distinct().order_by('category')

    html = render_to_string(
        'app/partials/question_detail.html',
        {
            'selected_question': selected_question,
            'categories': categories,
            'is_editing': is_editing,
            'edit_error': edit_error,
        },
        request=request,
    )
    return JsonResponse({
        'html': html,
        'question_id': selected_question.id,
        'title': selected_question.title,
        'is_editing': is_editing,
        'error': edit_error,
    })


@login_required
@require_http_methods(['POST'])
def question_delete_view(request: HttpRequest, question_id: int):
    question = Question.objects.filter(id=question_id).first()
    if not question:
        return JsonResponse({'success': False, 'error': 'Question not found.'}, status=404)

    success, error = handle_question_deletion(request, question)
    if not success:
        return JsonResponse({'success': False, 'error': error}, status=400)

    return JsonResponse({'success': True, 'deleted_id': question_id})
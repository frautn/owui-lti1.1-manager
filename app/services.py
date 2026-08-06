from typing import Optional, Tuple
from django.contrib.auth.models import User
from .models import Course, Question, QuestionFile, QuestionPicture


def create_question(*, user: User, course: Course, title: str) -> Question:
    """
    Creates and saves a new Question object.
    """
    return Question.objects.create(
        title=title,
        course=course,
        author=user,
        last_update=user,
    )


def handle_question_creation(request, course: Optional[Course]) -> Tuple[Optional[Question], Optional[str]]:
    """
    Validates post data and checks unique constraint (course + title).
    Returns a tuple: (created_question_or_none, error_message_or_none).
    """
    if not course:
        return None, "Cannot create a question without a selected course context."

    title = request.POST.get('title', '').strip()

    if not title:
        return None, "Question title cannot be empty."

    if Question.objects.filter(course=course, title=title).exists():
        return None, f"A question with the title '{title}' already exists in this course."

    question = create_question(user=request.user, course=course, title=title)
    return question, None


def update_question(
    *,
    question: Question,
    user: User,
    title: str,
    category: str = "General",
    prompt: str = "",
    notes: str = "",
) -> Question:
    """
    Updates and saves an existing Question object.
    """
    question.title = title
    question.category = category
    question.prompt = prompt
    question.notes = notes
    question.last_update = user
    question.save()
    return question


def handle_question_update(request, question: Question) -> Tuple[Optional[Question], Optional[str]]:
    """
    Validates post data for question editing and updates the question,
    including handling category, picture/file deletions, and new uploads.
    Returns a tuple: (updated_question_or_none, error_message_or_none).
    """
    title = request.POST.get('title', '').strip()
    category = request.POST.get('category', '').strip() or "General"
    prompt = request.POST.get('prompt', '').strip()
    notes = request.POST.get('notes', '').strip()

    if not title:
        return None, "Question title cannot be empty."

    if not category:
        return None, "Category cannot be empty."

    # Check unique title within the same course, excluding the current question
    if Question.objects.filter(course=question.course, title=title).exclude(id=question.id).exists():
        return None, f"A question with the title '{title}' already exists in this course."

    updated_question = update_question(
        question=question,
        user=request.user,
        title=title,
        category=category,
        prompt=prompt,
        notes=notes,
    )

    # 1. Delete checked body pictures
    delete_picture_ids = request.POST.getlist('delete_picture_ids')
    if delete_picture_ids:
        QuestionPicture.objects.filter(question=question, id__in=delete_picture_ids).delete()

    # 2. Delete checked file attachments
    delete_file_ids = request.POST.getlist('delete_file_ids')
    if delete_file_ids:
        QuestionFile.objects.filter(question=question, id__in=delete_file_ids).delete()

    # 3. Create new body pictures
    new_body_pictures = request.FILES.getlist('body_pictures')
    if new_body_pictures:
        last_order = question.body.order_by('-order').values_list('order', flat=True).first() or 0
        for idx, img in enumerate(new_body_pictures, start=last_order + 1):
            QuestionPicture.objects.create(
                question=question,
                image=img,
                order=idx,
            )

    # 4. Create new file attachments
    new_attachments = request.FILES.getlist('attachments')
    if new_attachments:
        for file_item in new_attachments:
            QuestionFile.objects.create(
                question=question,
                file=file_item,
            )

    return updated_question, None


def delete_question(*, question: Question) -> None:
    """
    Deletes a Question object from the database.
    """
    question.delete()


def handle_question_deletion(request, question: Question) -> Tuple[bool, Optional[str]]:
    """
    Handles question deletion.
    Returns a tuple: (success_boolean, error_message_or_none).
    """
    if not question:
        return False, "Question does not exist."

    try:
        delete_question(question=question)
        return True, None
    except Exception as e:
        return False, f"Could not delete question: {str(e)}"
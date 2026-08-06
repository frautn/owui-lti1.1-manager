from typing import Optional, Tuple
from django.contrib.auth.models import User
from .models import Course, Question


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

    # Check unique constraint (course + title)
    if Question.objects.filter(course=course, title=title).exists():
        return None, f"A question with the title '{title}' already exists in this course."

    question = create_question(user=request.user, course=course, title=title)
    return question, None

from typing import Optional, Tuple
from django.contrib.auth.models import User
from .models import Course, Question


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

    # Check unique constraint (course + title)
    if Question.objects.filter(course=course, title=title).exists():
        return None, f"A question with the title '{title}' already exists in this course."

    question = create_question(user=request.user, course=course, title=title)
    return question, None


def update_question(*, question: Question, user: User, title: str, prompt: str = "", notes: str = "") -> Question:
    """
    Updates and saves an existing Question object.
    """
    question.title = title
    question.prompt = prompt
    question.notes = notes
    question.last_update = user
    question.save()
    return question


def handle_question_update(request, question: Question) -> Tuple[Optional[Question], Optional[str]]:
    """
    Validates post data for question editing and updates the question.
    Returns a tuple: (updated_question_or_none, error_message_or_none).
    """
    title = request.POST.get('title', '').strip()
    prompt = request.POST.get('prompt', '').strip()
    notes = request.POST.get('notes', '').strip()

    if not title:
        return None, "Question title cannot be empty."

    # Check unique title within the same course, excluding the current question
    if Question.objects.filter(course=question.course, title=title).exclude(id=question.id).exists():
        return None, f"A question with the title '{title}' already exists in this course."

    updated_question = update_question(
        question=question,
        user=request.user,
        title=title,
        prompt=prompt,
        notes=notes,
    )
    return updated_question, None
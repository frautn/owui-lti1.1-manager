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
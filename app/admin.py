from django.contrib import admin

from .models import LtiCourseContext, Question


@admin.register(LtiCourseContext)
class LtiCourseContextAdmin(admin.ModelAdmin):
	list_display = ('moodle_site', 'course_id', 'course_title', 'updated_at')
	search_fields = ('moodle_site', 'course_id', 'course_title')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'last_update', 'updated_at')
	search_fields = ('title', 'prompt', 'notes')

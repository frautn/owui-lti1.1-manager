from django.contrib import admin

from .models import LtiCourseContext


@admin.register(LtiCourseContext)
class LtiCourseContextAdmin(admin.ModelAdmin):
	list_display = ('moodle_site', 'course_id', 'course_title', 'updated_at')
	search_fields = ('moodle_site', 'course_id', 'course_title')

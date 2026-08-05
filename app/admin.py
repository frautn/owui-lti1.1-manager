from django.contrib import admin

from .models import Course, Question, Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
	list_display = ('moodle_site', 'custom_moodle_site')
	search_fields = ('moodle_site', 'custom_moodle_site')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ('site', 'course_id', 'course_title', 'updated_at')
	search_fields = ('course_id', 'course_title')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'last_update', 'updated_at')
	search_fields = ('title', 'prompt', 'notes')

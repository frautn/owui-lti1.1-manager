from django.contrib import admin

from .models import Site, Course, Question, QuestionPicture, QuestionFile



@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
	list_display = ('moodle_site', 'custom_moodle_site')
	search_fields = ('moodle_site', 'custom_moodle_site')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ('site', 'course_id', 'course_title', 'updated_at')
	search_fields = ('course_id', 'course_title')


# Allow managing pictures directly on the Question admin page
class QuestionPictureInline(admin.TabularInline):
    model = QuestionPicture
    extra = 1


# Allow managing files directly on the Question admin page
class QuestionFileInline(admin.TabularInline):
    model = QuestionFile
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'course', 'author', 'updated_at')
    list_filter = ('course', 'category')
    search_fields = ('title', 'prompt', 'notes')
    inlines = [QuestionPictureInline, QuestionFileInline]


# Optionally register them individually if you want dedicated admin list pages
@admin.register(QuestionPicture)
class QuestionPictureAdmin(admin.ModelAdmin):
    list_display = ('question', 'image', 'order', 'uploaded_at')


@admin.register(QuestionFile)
class QuestionFileAdmin(admin.ModelAdmin):
    list_display = ('question', 'file', 'uploaded_at')


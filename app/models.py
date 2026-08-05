from django.conf import settings
from django.db import models


class Site(models.Model):
	moodle_site = models.CharField(max_length=255, unique=True)
	custom_moodle_site = models.CharField(max_length=255, blank=True, help_text="Optional display name for this Moodle site.")

	def __str__(self) -> str:
		return self.custom_moodle_site or self.moodle_site


class Course(models.Model):
	site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='courses')
	course_id = models.CharField(max_length=255)
	course_title = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['site', 'course_title'],
				name='uniq_course_site_title',
			)
		]

	def __str__(self) -> str:
		name = self.course_title or self.course_id
		return f"{self.site} - {name}"


class Question(models.Model):
	title = models.CharField(max_length=255)
	prompt = models.TextField(blank=True, help_text="Prompt content to send to LLMs.")
	notes = models.TextField(blank=True)
	course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='authored_prompts',
	)
	last_update = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='updated_prompts',
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['course', 'title'],
				name='uniq_question_course_title',
			)
		]

	def __str__(self) -> str:
		return self.title

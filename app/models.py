from django.db import models


class LtiCourseContext(models.Model):
	moodle_site = models.CharField(max_length=255)
	course_id = models.CharField(max_length=255)
	course_title = models.CharField(max_length=255, blank=True)
	custom_moodle_site = models.CharField(max_length=255, null=True, blank=False, help_text="Optional custom Moodle site name for display purposes.")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['moodle_site', 'course_id'],
				name='uniq_lti_course_context_site_course',
			)
		]

	def __str__(self) -> str:
		if self.course_title:
			if self.custom_moodle_site:
				return f"{self.custom_moodle_site} - {self.course_title} ({self.course_id})"
			else:
				return f"{self.moodle_site} - {self.course_title} ({self.course_id})"
		return f"{self.moodle_site} - {self.course_id}"

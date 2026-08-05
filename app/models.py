from django.db import models


class LtiCourseContext(models.Model):
	moodle_site = models.CharField(max_length=255)
	course_id = models.CharField(max_length=255)
	course_title = models.CharField(max_length=255, blank=True)
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
			return f"{self.moodle_site} - {self.course_title} ({self.course_id})"
		return f"{self.moodle_site} - {self.course_id}"

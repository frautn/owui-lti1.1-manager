from django.urls import path

from .views import home_view, lti_launch_view

urlpatterns = [
    path('', home_view, name='home'),
    path('lti/launch/', lti_launch_view, name='lti-launch'),
]

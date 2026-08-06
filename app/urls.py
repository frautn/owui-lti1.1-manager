from django.urls import path
from django.contrib.auth.views import LoginView

from .views import home_view, lti_launch_view, logout_view, question_detail_partial_view, question_delete_view

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='app/login.html', redirect_authenticated_user=True),
        name='login',
    ),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('questions/<int:question_id>/partial/', question_detail_partial_view, name='question-detail-partial'),
    path('questions/<int:question_id>/delete/', question_delete_view, name='question-delete'),
    path('lti/launch/', lti_launch_view, name='lti-launch'),
]

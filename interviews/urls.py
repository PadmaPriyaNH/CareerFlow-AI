from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.interview_setup, name='interview_setup'),
    path('<int:session_id>/', views.interview_room, name='interview_room'),
    path('<int:session_id>/submit/<int:question_id>/', views.submit_answer, name='submit_answer'),
    path('<int:session_id>/feedback/', views.interview_feedback, name='interview_feedback'),
    path('<int:session_id>/stop/', views.stop_interview, name='stop_interview'),
]

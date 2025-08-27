from django.urls import path
from . import views

urlpatterns = [
    path('', views.assignments_view, name='assignments'),
    path('create/', views.create_assignment, name='create_assignment'),
    path('<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('<int:pk>/take/', views.take_assignment, name='take_assignment'),
    path('<int:pk>/questions/', views.add_questions, name='add_questions'),
    path('<int:pk>/submissions/', views.view_submissions, name='view_submissions'),
    path('<int:pk>/grade/<int:student_id>/', views.grade_submission, name='grade_submission'),
     path('<int:pk>/publish/', views.publish_assignment, name='publish_assignment'),
]
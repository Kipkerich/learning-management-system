from django.urls import path
from . import views

urlpatterns = [
    # Trainer Unit Assignment URLs (Admin)
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:pk>/edit/', views.edit_assignment, name='edit_assignment'),
    path('assignments/<int:pk>/delete/', views.delete_assignment, name='delete_assignment'),

    # Trainer Portal / Results Entry
    path('trainer/', views.trainer_portal, name='trainer_portal'),
    path('trainer/enter-results/<int:assignment_id>/', views.enter_results, name='enter_results'),

    # Admin Results Management
    path('admin/results/', views.admin_results_list, name='admin_results_list'),
    path('admin/results/<int:pk>/edit/', views.admin_edit_result, name='admin_edit_result'),
    path('admin/results/<int:pk>/delete/', views.admin_delete_result, name='admin_delete_result'),
    path('admin/results/<int:pk>/toggle-publish/', views.publish_results_toggle, name='publish_results_toggle'),

    # Transcripts & Graduation Eligibility
    path('student/<int:student_id>/transcript/', views.transcript_detail, name='transcript_detail'),
    path('student/<int:student_id>/graduation/', views.manage_graduation, name='manage_graduation'),
    path('my-results/', views.student_my_results, name='student_my_results'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.resources_view, name='resources'),
    path('add/', views.add_resource, name='add_resource'),
    path('<int:pk>/', views.resource_detail, name='resource_detail'),
    path('<int:pk>/edit/', views.edit_resource, name='edit_resource'),
    path('<int:pk>/delete/', views.delete_resource, name='delete_resource'),
    path('<int:pk>/download/', views.download_resource, name='download_resource'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('<int:course_pk>/units/add/', views.add_unit, name='add_unit'),
    path('units/<int:pk>/edit/', views.edit_unit, name='edit_unit'),
    path('units/<int:pk>/delete/', views.delete_unit, name='delete_unit'),
    path('set-fee/', views.set_course_fee, name='set_course_fee'),
]

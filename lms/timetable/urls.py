from django.urls import path
from . import views

urlpatterns = [
    path('', views.timetable_view, name='timetable'),
    path('create/', views.create_timetable, name='create_timetable'),
    path('edit/<int:pk>/', views.edit_timetable, name='edit_timetable'),
    path('delete/<int:pk>/', views.delete_timetable, name='delete_timetable'),
    path('api/json/', views.timetable_json, name='timetable_json'),
    path('api/units/', views.get_units_by_course, name='api_get_units'),
    path('rooms/', views.manage_rooms, name='manage_rooms'),
    path('rooms/edit/<int:pk>/', views.edit_room, name='edit_room'),
    path('rooms/delete/<int:pk>/', views.delete_room, name='delete_room'),
]
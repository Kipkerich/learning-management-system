from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .api_views import UserProfileDetail, UserProfileUpdate
from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
    path('admin/register/', views.admin_register_view, name='admin_register'),
    path('admin/users/', views.user_list_view, name='user_list'),
    path('admin/users/<int:pk>/', views.user_detail_view, name='user_detail'),
    path('admin/users/<int:pk>/edit/', views.edit_user_view, name='edit_user'),
    path('admin/users/<int:pk>/delete/', views.delete_user_view, name='delete_user'),
    path('admin/users/<int:pk>/toggle-status/', views.toggle_user_status_view, name='toggle_user_status'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
     path('api/profile/', UserProfileDetail.as_view(), name='api_profile'),
    path('api/profile/update/', UserProfileUpdate.as_view(), name='api_profile_update'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cats/', views.cats_view, name='cats'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
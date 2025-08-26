from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .api_views import UserProfileDetail, UserProfileUpdate

urlpatterns = [
    path('admin/register/', views.admin_register_view, name='admin_register'),
    path('admin/users/', views.user_list_view, name='user_list'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
     path('api/profile/', UserProfileDetail.as_view(), name='api_profile'),
    path('api/profile/update/', UserProfileUpdate.as_view(), name='api_profile_update'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cats/', views.cats_view, name='cats'),
]
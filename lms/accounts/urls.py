from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/register/', views.admin_register_view, name='admin_register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
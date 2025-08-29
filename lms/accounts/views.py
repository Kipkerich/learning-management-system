from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .forms import AdminUserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib import messages


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_register_view(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('user_list')  # Redirect to user list page
    else:
        form = AdminUserCreationForm()
    return render(request, 'accounts/admin_register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to home after login
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    
    return render(request, 'accounts/profile.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    users = User.objects.all().select_related('userprofile')
    
    # Filter by user type if provided
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(userprofile__user_type=user_type)
    
    # Calculate statistics
    students_count = UserProfile.objects.filter(user_type='student').count()
    trainers_count = UserProfile.objects.filter(user_type='trainer').count()
    admins_count = UserProfile.objects.filter(user_type='admin').count()
    
    context = {
        'users': users,
        'students_count': students_count,
        'trainers_count': trainers_count,
        'admins_count': admins_count,
    }
    
    return render(request, 'accounts/user_list.html', context)

@login_required
@user_passes_test(is_admin)
def user_detail_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def edit_user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.userprofile
    
    if request.method == 'POST':
        # Update user fields
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = 'is_active' in request.POST
        
        # Handle password change if provided
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password == confirm_password:
                if len(new_password) >= 8:  # Minimum password length check
                    user.set_password(new_password)
                    messages.success(request, 'Password updated successfully.')
                else:
                    messages.error(request, 'Password must be at least 8 characters long.')
            else:
                messages.error(request, 'Passwords do not match.')
        
        # Update profile fields if they exist
        if hasattr(user, 'userprofile'):
            user.userprofile.user_type = request.POST.get('user_type', 'student')
            user.userprofile.save()
        
        user.save()
        
        messages.success(request, f'User {user.username} updated successfully.')
        return redirect('user_list')
    
    return render(request, 'accounts/edit_user.html', {'user': user, 'profile': profile})

@login_required
@user_passes_test(is_admin)
def delete_user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        if not user.is_superuser:
            username = user.username
            user.delete()
            messages.success(request, f'User {username} deleted successfully.')
        else:
            messages.error(request, 'Cannot delete superuser accounts.')
        return redirect('user_list')
    
    return render(request, 'accounts/delete_user.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def toggle_user_status_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.username} {status} successfully.')
    
    return redirect('user_list')


@login_required
def cats_view(request):
    return render(request, 'cats.html')
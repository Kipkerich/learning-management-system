from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .forms import AdminUserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
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
@user_passes_test(is_superuser)
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
def timetable_view(request):
    return render(request, 'timetable.html')


@login_required
def cats_view(request):
    return render(request, 'cats.html')
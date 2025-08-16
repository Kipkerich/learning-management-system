from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .forms import AdminUserCreationForm

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_register_view(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('admin:index')  # Redirect to admin panel
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
                return redirect('home')  # Redirect to home after login
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def home_view(request):
    
    return render(request, 'index.html')

@login_required
def profile_view(request):
    
    return render(request, 'accounts/profile.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout
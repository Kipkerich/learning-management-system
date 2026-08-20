from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm

from finance.models import Invoice, FeeStructure
from courses.models import Course
from .forms import AdminUserCreationForm, UserCreationForm, StudentProfileForm, StudentUserEditForm, CohortForm
from django.contrib.auth.models import User
from .models import UserProfile, StudentProfile, Cohort
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone


def create_superuser_view(request):
    if User.objects.filter(is_superuser=True).exists():
        return JsonResponse({"error": "Superuser already exists"}, status=400)

    user = User.objects.create_superuser(
        username="manager",
        email="manager@example.com",
        password="Super@123"
    )
    return JsonResponse({"success": f"Superuser '{user.username}' created"})


def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin'


@user_passes_test(is_admin)
def admin_register_view(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('user_list')
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
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@user_passes_test(is_admin)
def register_student(request):
    if not is_admin(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = StudentProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Save the User
                    user = user_form.save()
                    
                    # 2. Attach Profile to that User
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    
                    # AUTOMATIC BILLING BASED ON COURSE
                    if profile.course:
                        fee_type, _ = FeeStructure.objects.get_or_create(
                            name=profile.course.name,
                            defaults={'amount': profile.course.school_fee, 'description': profile.course.description}
                        )
                        Invoice.objects.create(
                            student=profile,
                            fee_type=fee_type
                        )
                    
                messages.success(request, f"Student {user.get_full_name() or user.username} registered successfully.")
                return redirect('student_list')
            except Exception as e:
                user_form.add_error(None, f"An error occurred: {e}")
        else:
            messages.error(request, "Please correct the highlighted errors below before submitting.")
    else:
        user_form = UserCreationForm()
        profile_form = StudentProfileForm(initial={'enrollment_date': timezone.now().date()})
        
    courses = Course.objects.all()

    return render(request, 'accounts/register_student.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'courses': courses
    })


@user_passes_test(is_admin)
def student_list(request):
    if not is_admin(request.user):
        return redirect('dashboard')
        
    all_students = StudentProfile.objects.all().select_related('user', 'course', 'cohort')

    # Categorize students by Course, and sub-categorize by Cohort
    grouped_directory = []
    course_buckets = {}

    for student in all_students:
        c_id = student.course.id if student.course else None
        c_name = student.course.name if student.course else "Unassigned Course"
        coh_id = student.cohort.id if student.cohort else None
        coh_name = student.cohort.name if student.cohort else "Unassigned Cohort"

        if c_id not in course_buckets:
            course_buckets[c_id] = {
                'course': student.course,
                'course_name': c_name,
                'cohort_map': {}
            }

        if coh_id not in course_buckets[c_id]['cohort_map']:
            course_buckets[c_id]['cohort_map'][coh_id] = {
                'cohort': student.cohort,
                'cohort_name': coh_name,
                'students': []
            }

        course_buckets[c_id]['cohort_map'][coh_id]['students'].append(student)

    for c_id, c_data in course_buckets.items():
        cohort_list_data = []
        for coh_id, coh_data in c_data['cohort_map'].items():
            cohort_list_data.append(coh_data)

        grouped_directory.append({
            'course': c_data['course'],
            'course_name': c_data['course_name'],
            'cohort_groups': cohort_list_data,
            'total_students': sum(len(cg['students']) for cg in cohort_list_data)
        })

    return render(request, 'accounts/student_list.html', {
        'grouped_directory': grouped_directory,
        'all_students': all_students,
        'total_count': all_students.count()
    })


@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    return render(request, 'accounts/student_detail.html', {'student': student})


@user_passes_test(is_admin)
def edit_student(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    user = student.user

    if request.method == 'POST':
        user_form = StudentUserEditForm(request.POST, instance=user)
        profile_form = StudentProfileForm(request.POST, instance=student)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f"Student profile for {user.get_full_name() or user.username} updated successfully.")
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, "Please correct the highlighted errors below before saving.")
    else:
        user_form = StudentUserEditForm(instance=user)
        profile_form = StudentProfileForm(instance=student)

    return render(request, 'accounts/edit_student.html', {
        'student': student,
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
@user_passes_test(is_admin)
def cohort_list(request):
    cohorts = Cohort.objects.all().prefetch_related('students')
    return render(request, 'accounts/cohort_list.html', {'cohorts': cohorts})


@login_required
@user_passes_test(is_admin)
def create_cohort(request):
    if request.method == 'POST':
        form = CohortForm(request.POST)
        if form.is_valid():
            cohort = form.save()
            messages.success(request, f"Cohort '{cohort.name}' created successfully.")
            return redirect('cohort_list')
    else:
        form = CohortForm()
    return render(request, 'accounts/cohort_form.html', {'form': form, 'title': 'Create New Cohort'})


@login_required
@user_passes_test(is_admin)
def edit_cohort(request, pk):
    cohort = get_object_or_404(Cohort, pk=pk)
    if request.method == 'POST':
        form = CohortForm(request.POST, instance=cohort)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cohort '{cohort.name}' updated successfully.")
            return redirect('cohort_list')
    else:
        form = CohortForm(instance=cohort)
    return render(request, 'accounts/cohort_form.html', {'form': form, 'cohort': cohort, 'title': f'Edit {cohort.name}'})


@login_required
@user_passes_test(is_admin)
def delete_cohort(request, pk):
    cohort = get_object_or_404(Cohort, pk=pk)
    if request.method == 'POST':
        name = cohort.name
        cohort.delete()
        messages.warning(request, f"Cohort '{name}' deleted.")
        return redirect('cohort_list')
    return render(request, 'accounts/cohort_confirm_delete.html', {'cohort': cohort})


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
    return redirect('login')


@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    users = User.objects.all().select_related('userprofile')
    
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(userprofile__user_type=user_type)
    
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
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = 'is_active' in request.POST
        
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password == confirm_password:
                if len(new_password) >= 8:
                    user.set_password(new_password)
                    messages.success(request, 'Password updated successfully.')
                else:
                    messages.error(request, 'Password must be at least 8 characters long.')
            else:
                messages.error(request, 'Passwords do not match.')
        
        new_user_type = request.POST.get('user_type', 'student')
        if new_user_type == 'admin':
            user.is_staff = True
        elif not user.is_superuser and user.is_staff and new_user_type != 'admin':
            user.is_staff = False

        if hasattr(user, 'userprofile'):
            user.userprofile.user_type = new_user_type
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

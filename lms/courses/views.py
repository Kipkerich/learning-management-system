from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Course, Unit
from .forms import CourseForm, UnitForm, CourseFeeUpdateForm

def is_staff_user(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin'

@login_required
@user_passes_test(is_staff_user)
def course_list(request):
    courses = Course.objects.all().prefetch_related('units')
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
@user_passes_test(is_staff_user)
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    units = course.units.all()
    return render(request, 'courses/course_detail.html', {'course': course, 'units': units})


@login_required
@user_passes_test(is_staff_user)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.name}' created successfully.")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Add New Course'})


@login_required
@user_passes_test(is_staff_user)
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.name}' updated successfully.")
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'course': course, 'title': f'Edit {course.name}'})


@login_required
@user_passes_test(is_staff_user)
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        name = course.name
        course.delete()
        messages.warning(request, f"Course '{name}' deleted successfully.")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
@user_passes_test(is_staff_user)
def add_unit(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.course = course
            unit.save()
            messages.success(request, f"Unit '{unit.name}' added to {course.name}.")
            return redirect('course_detail', pk=course.pk)
    else:
        form = UnitForm()
    return render(request, 'courses/unit_form.html', {'form': form, 'course': course, 'title': f'Add Unit to {course.name}'})


@login_required
@user_passes_test(is_staff_user)
def edit_unit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Unit '{unit.name}' updated successfully.")
            return redirect('course_detail', pk=unit.course.pk)
    else:
        form = UnitForm(instance=unit)
    return render(request, 'courses/unit_form.html', {'form': form, 'course': unit.course, 'unit': unit, 'title': f'Edit Unit {unit.name}'})


@login_required
@user_passes_test(is_staff_user)
def delete_unit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    course_pk = unit.course.pk
    if request.method == 'POST':
        name = unit.name
        unit.delete()
        messages.warning(request, f"Unit '{name}' deleted.")
        return redirect('course_detail', pk=course_pk)
    return render(request, 'courses/unit_confirm_delete.html', {'unit': unit})


@login_required
@user_passes_test(is_staff_user)
def set_course_fee(request):
    if request.method == 'POST':
        form = CourseFeeUpdateForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            new_fee = form.cleaned_data['school_fee']
            course.school_fee = new_fee
            course.save()
            messages.success(request, f"School fee for '{course.name}' updated to KES {new_fee:,.2f}.")
            return redirect('course_list')
    else:
        initial_course_id = request.GET.get('course_id')
        initial_data = {}
        if initial_course_id:
            course = Course.objects.filter(pk=initial_course_id).first()
            if course:
                initial_data = {'course': course, 'school_fee': course.school_fee}
        form = CourseFeeUpdateForm(initial=initial_data)
    return render(request, 'courses/set_fee.html', {'form': form})

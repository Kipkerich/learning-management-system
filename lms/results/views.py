from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import TrainerUnitAssignment, StudentResult
from .forms import TrainerUnitAssignmentForm, StudentResultEntryForm, GraduationEligibilityForm
from courses.models import Unit, Course
from accounts.models import Cohort, StudentProfile, UserProfile
from django.contrib.auth.models import User

def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin'

def is_trainer_or_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.user_type in ['admin', 'trainer']):
        return True
    return False


# ==========================================
# 1. TRAINER UNIT ASSIGNMENTS (ADMIN MODULE)
# ==========================================

@login_required
@user_passes_test(is_admin)
def assignment_list(request):
    assignments = TrainerUnitAssignment.objects.all().select_related('trainer', 'unit', 'unit__course', 'cohort')
    return render(request, 'results/assignment_list.html', {'assignments': assignments})


@login_required
@user_passes_test(is_admin)
def create_assignment(request):
    if request.method == 'POST':
        form = TrainerUnitAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            messages.success(
                request,
                f"Assigned '{assignment.unit.name}' ({assignment.cohort.name}) to Trainer {assignment.trainer.get_full_name() or assignment.trainer.username}."
            )
            return redirect('assignment_list')
    else:
        form = TrainerUnitAssignmentForm()
    return render(request, 'results/assignment_form.html', {'form': form, 'title': 'Assign Unit to Trainer'})


@login_required
@user_passes_test(is_admin)
def edit_assignment(request, pk):
    assignment = get_object_or_404(TrainerUnitAssignment, pk=pk)
    if request.method == 'POST':
        form = TrainerUnitAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer unit assignment updated successfully.")
            return redirect('assignment_list')
    else:
        form = TrainerUnitAssignmentForm(instance=assignment)
    return render(request, 'results/assignment_form.html', {'form': form, 'title': 'Edit Trainer Unit Assignment'})


@login_required
@user_passes_test(is_admin)
def delete_assignment(request, pk):
    assignment = get_object_or_404(TrainerUnitAssignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.warning(request, "Trainer unit assignment removed.")
        return redirect('assignment_list')
    return render(request, 'results/assignment_confirm_delete.html', {'assignment': assignment})


# ==========================================
# 2. TRAINER RESULT ENTRY PORTAL
# ==========================================

@login_required
@user_passes_test(is_trainer_or_admin)
def trainer_portal(request):
    """Lists unit assignments for the logged-in trainer."""
    if is_admin(request.user):
        assignments = TrainerUnitAssignment.objects.all().select_related('trainer', 'unit', 'unit__course', 'cohort')
    else:
        assignments = TrainerUnitAssignment.objects.filter(trainer=request.user).select_related('unit', 'unit__course', 'cohort')

    return render(request, 'results/trainer_portal.html', {'assignments': assignments})


@login_required
@user_passes_test(is_trainer_or_admin)
def enter_results(request, assignment_id):
    assignment = get_object_or_404(TrainerUnitAssignment, pk=assignment_id)

    # Restrict non-admin trainers to their own assignments
    if not is_admin(request.user) and assignment.trainer != request.user:
        messages.error(request, "You are not authorized to enter results for this unit assignment.")
        return redirect('trainer_portal')

    # Get students enrolled in the course matching this unit and in this cohort
    course = assignment.unit.course
    # Find CourseFee or Course matching name
    from finance.models import CourseFee
    course_fee = CourseFee.objects.filter(course_name__iexact=course.name).first()

    students = StudentProfile.objects.filter(cohort=assignment.cohort).select_related('user')
    if course_fee:
        students = students.filter(Q(course=course_fee) | Q(course__course_name__iexact=course.name))

    if request.method == 'POST':
        # Process CAT and Exam scores submitted
        saved_count = 0
        for student in students:
            cat_val = request.POST.get(f'cat_{student.id}', '0')
            exam_val = request.POST.get(f'exam_{student.id}', '0')

            try:
                cat_score = float(cat_val) if cat_val else 0.0
                exam_score = float(exam_val) if exam_val else 0.0
            except ValueError:
                cat_score, exam_score = 0.0, 0.0

            result_obj, created = StudentResult.objects.get_or_create(
                student=student,
                unit=assignment.unit,
                defaults={
                    'cohort': assignment.cohort,
                    'cat_score': cat_score,
                    'exam_score': exam_score
                }
            )
            if not created:
                result_obj.cohort = assignment.cohort
                result_obj.cat_score = cat_score
                result_obj.exam_score = exam_score
                result_obj.save()
            saved_count += 1

        messages.success(request, f"Results recorded for {saved_count} student(s) in {assignment.unit.code}.")
        return redirect('trainer_portal')

    # Existing results lookup
    existing_results = {
        r.student_id: r for r in StudentResult.objects.filter(unit=assignment.unit, cohort=assignment.cohort)
    }

    student_rows = []
    for student in students:
        res = existing_results.get(student.id)
        student_rows.append({
            'student': student,
            'cat_score': res.cat_score if res else 0.0,
            'exam_score': res.exam_score if res else 0.0,
            'total_score': res.total_score if res else 0.0,
            'grade': res.grade if res else 'N/A',
            'is_published': res.is_published if res else False,
            'verified': res.verified_by_admin if res else False
        })

    return render(request, 'results/enter_results.html', {
        'assignment': assignment,
        'student_rows': student_rows
    })


# ==========================================
# 3. ADMIN RESULTS MANAGEMENT & VERIFICATION
# ==========================================

@login_required
@user_passes_test(is_admin)
def admin_results_list(request):
    selected_cohort_id = request.GET.get('cohort')
    selected_course_name = request.GET.get('course')
    selected_student_id = request.GET.get('student')

    cohorts = Cohort.objects.all()
    selected_cohort = None
    selected_course = None
    selected_student = None

    courses_list = []
    students_list = []
    student_results = []

    if selected_cohort_id:
        selected_cohort = get_object_or_404(Cohort, pk=selected_cohort_id)
        # Find all distinct courses for students in this cohort
        from finance.models import CourseFee
        students_in_cohort = StudentProfile.objects.filter(cohort=selected_cohort).select_related('course', 'user')

        # Build list of distinct courses present in this cohort
        course_names = set(s.course.course_name for s in students_in_cohort if s.course)
        courses_list = CourseFee.objects.filter(course_name__in=course_names)

        if selected_course_name:
            selected_course = CourseFee.objects.filter(course_name=selected_course_name).first()
            students_list = students_in_cohort.filter(course__course_name=selected_course_name)

            if selected_student_id:
                selected_student = get_object_or_404(StudentProfile, pk=selected_student_id)
                student_results = StudentResult.objects.filter(
                    student=selected_student,
                    cohort=selected_cohort
                ).select_related('unit', 'unit__course')

    context = {
        'cohorts': cohorts,
        'selected_cohort': selected_cohort,
        'courses_list': courses_list,
        'selected_course': selected_course,
        'selected_course_name': selected_course_name,
        'students_list': students_list,
        'selected_student': selected_student,
        'student_results': student_results,
    }
    return render(request, 'results/admin_results_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_result(request, pk):
    result = get_object_or_404(StudentResult, pk=pk)
    if request.method == 'POST':
        form = StudentResultEntryForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, f"Result updated for {result.student.user.get_full_name()} ({result.unit.code}).")
            return redirect('admin_results_list')
    else:
        form = StudentResultEntryForm(instance=result)
    return render(request, 'results/admin_edit_result.html', {'form': form, 'result': result})


@login_required
@user_passes_test(is_admin)
def admin_delete_result(request, pk):
    result = get_object_or_404(StudentResult, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.warning(request, "Student result record deleted.")
        return redirect('admin_results_list')
    return render(request, 'results/result_confirm_delete.html', {'result': result})


@login_required
@user_passes_test(is_admin)
def publish_results_toggle(request, pk):
    result = get_object_or_404(StudentResult, pk=pk)
    result.is_published = not result.is_published
    result.save()
    status = "published" if result.is_published else "unpublished"
    messages.success(request, f"Result for {result.student.admission_number} ({result.unit.code}) {status}.")
    return redirect('admin_results_list')


# ==========================================
# 4. TRANSCRIPTS & GRADUATION ELIGIBILITY
# ==========================================

@login_required
def transcript_detail(request, student_id):
    student = get_object_or_404(StudentProfile.objects.select_related('user', 'course', 'cohort'), pk=student_id)

    # Permission check: Student can only view their own transcript, Admin can view any
    if not is_admin(request.user) and student.user != request.user:
        messages.error(request, "Access denied. You can only view your own transcript.")
        return redirect('dashboard')

    # Query results: Students only see published results unless admin
    results = student.results.select_related('unit', 'cohort', 'unit__course').all()
    if not is_admin(request.user):
        results = results.filter(is_published=True)

    total_units = results.count()
    passed_units = sum(1 for r in results if r.total_score >= 40)
    avg_score = sum(r.total_score for r in results) / total_units if total_units > 0 else 0.0

    return render(request, 'results/transcript_detail.html', {
        'student': student,
        'results': results,
        'total_units': total_units,
        'passed_units': passed_units,
        'avg_score': avg_score,
        'is_admin_view': is_admin(request.user)
    })


@login_required
@user_passes_test(is_admin)
def manage_graduation(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    if request.method == 'POST':
        form = GraduationEligibilityForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Graduation eligibility status updated for {student.user.get_full_name()}.")
            return redirect('student_detail', pk=student.pk)
    else:
        form = GraduationEligibilityForm(instance=student)
    return render(request, 'results/manage_graduation.html', {'form': form, 'student': student})


@login_required
def student_my_results(request):
    """View for logged-in student to check published CAT & Exam results."""
    if not hasattr(request.user, 'student_profile'):
        messages.warning(request, "You do not have a student profile associated with your account.")
        return redirect('dashboard')

    student = request.user.student_profile
    published_results = student.results.filter(is_published=True).select_related('unit', 'unit__course', 'cohort')

    return render(request, 'results/student_my_results.html', {
        'student': student,
        'results': published_results
    })

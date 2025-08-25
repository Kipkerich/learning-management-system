# assignments/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Assignment, Question, StudentAnswer, StudentAssignment
from .forms import AssignmentForm, QuestionForm, ChoiceFormSet, StudentAnswerForm

def is_trainer(user):
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'trainer'

@login_required
def assignments_view(request):
    assignments = Assignment.objects.filter(is_published=True)
    
    if is_trainer(request.user):
        assignments = Assignment.objects.all()
    
    # Get student submissions
    submissions = {}
    if not is_trainer(request.user):
        submissions = {
            sub.assignment_id: sub 
            for sub in StudentAssignment.objects.filter(student=request.user)
        }
    
    context = {
        'assignments': assignments,
        'is_trainer': is_trainer(request.user),
        'submissions': submissions,
        'now': timezone.now()
    }
    return render(request, 'assignments/assignments.html', context)

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if not assignment.is_published and not is_trainer(request.user):
        messages.error(request, "This assignment is not available.")
        return redirect('assignments')
    
    # Check if student has already submitted
    student_submission = None
    if not is_trainer(request.user):
        student_submission = StudentAssignment.objects.filter(
            student=request.user, assignment=assignment
        ).first()
    
    context = {
        'assignment': assignment,
        'is_trainer': is_trainer(request.user),
        'student_submission': student_submission,
        'now': timezone.now()
    }
    return render(request, 'assignments/assignment_detail.html', context)


@login_required
def take_assignment(request, pk):
    if is_trainer(request.user):
        messages.error(request, "Trainers cannot take assignments.")
        return redirect('assignments')
    
    assignment = get_object_or_404(Assignment, pk=pk, is_published=True)
    
    # Check if already submitted
    submission = StudentAssignment.objects.filter(
        student=request.user, assignment=assignment
    ).first()
    
    if submission:
        messages.info(request, "You have already submitted this assignment.")
        return redirect('assignment_detail', pk=pk)
    
    # Check if due date passed
    if timezone.now() > assignment.due_date:
        messages.error(request, "The due date for this assignment has passed.")
        return redirect('assignment_detail', pk=pk)
    
    questions = assignment.questions.all()
    
    if request.method == 'POST':
        valid = True
        
        # Save all answers
        for question in questions:
            form = StudentAnswerForm(request.POST, question=question, prefix=f"q{question.id}")
            if form.is_valid():
                answer, created = StudentAnswer.objects.get_or_create(
                    student=request.user,
                    assignment=assignment,
                    question=question
                )
                
                if assignment.assignment_type == 'multiple_choice':
                    answer.selected_choice = form.cleaned_data.get('selected_choice')
                    answer.answer_text = ''  # Clear text answer for MC questions
                else:
                    answer.answer_text = form.cleaned_data.get('answer_text', '')
                    answer.selected_choice = None  # Clear choice for text questions
                
                answer.is_submitted = True
                answer.save()
            else:
                valid = False
                # You might want to add error handling here
        
        if valid:
            # Create submission record
            StudentAssignment.objects.create(
                student=request.user,
                assignment=assignment
            )
            messages.success(request, "Assignment submitted successfully!")
            return redirect('assignment_detail', pk=pk)
        else:
            messages.error(request, "Please fill in all required fields.")
    
    # Prepare forms for each question
    question_forms = []
    for question in questions:
        initial = {}
        existing_answer = StudentAnswer.objects.filter(
            student=request.user,
            assignment=assignment,
            question=question
        ).first()
        
        if existing_answer:
            if assignment.assignment_type == 'multiple_choice':
                initial['selected_choice'] = existing_answer.selected_choice
            else:
                initial['answer_text'] = existing_answer.answer_text
        
        form = StudentAnswerForm(question=question, prefix=f"q{question.id}", initial=initial)
        question_forms.append((question, form))
    
    context = {
        'assignment': assignment,
        'question_forms': question_forms,
    }
    return render(request, 'assignments/take_assignment.html', context)


# Trainer Views
@login_required
def create_assignment(request):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can create assignments.")
        return redirect('assignments')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('add_questions', pk=assignment.pk)
    else:
        form = AssignmentForm()
    
    context = {'form': form}
    return render(request, 'assignments/create_assignment.html', context)

@login_required
def add_questions(request, pk):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can add questions.")
        return redirect('assignments')
    
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.assignment = assignment
            question.save()
            
            if assignment.assignment_type == 'multiple_choice':
                formset = ChoiceFormSet(request.POST, instance=question)
                if formset.is_valid():
                    formset.save()
            
            messages.success(request, 'Question added successfully!')
            return redirect('add_questions', pk=assignment.pk)
    else:
        question_form = QuestionForm()
    
    questions = assignment.questions.all()
    context = {
        'assignment': assignment,
        'question_form': question_form,
        'questions': questions,
    }
    return render(request, 'assignments/add_questions.html', context)

@login_required
def view_submissions(request, pk):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can view submissions.")
        return redirect('assignments')
    
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    submissions = StudentAssignment.objects.filter(assignment=assignment)
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'assignments/view_submissions.html', context)

@login_required
def grade_submission(request, pk, student_id):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can grade submissions.")
        return redirect('assignments')
    
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    submission = get_object_or_404(StudentAssignment, assignment=assignment, student_id=student_id)
    answers = StudentAnswer.objects.filter(assignment=assignment, student_id=student_id)
    
    if request.method == 'POST':
        submission.feedback = request.POST.get('feedback', '')
        submission.is_graded = True
        submission.calculate_score()
        submission.save()
        messages.success(request, 'Submission graded successfully!')
        return redirect('view_submissions', pk=assignment.pk)
    
    context = {
        'assignment': assignment,
        'submission': submission,
        'answers': answers,
    }
    return render(request, 'assignments/grade_submission.html', context)
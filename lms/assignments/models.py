# assignments/models.py
from django.db import models
from django.contrib.auth.models import User
import os

class Assignment(models.Model):
    ASSIGNMENT_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('text_input', 'Text Input'),
        ('file_upload', 'File Upload'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    total_marks = models.PositiveIntegerField(default=100)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    marks = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

class StudentAnswer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    answer_text = models.TextField(blank=True)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'question']

    def __str__(self):
        return f"{self.student.username} - {self.question}"

class StudentAssignment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    total_marks_obtained = models.PositiveIntegerField(default=0)
    is_graded = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'assignment']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    def calculate_score(self):
        answers = StudentAnswer.objects.filter(
            student=self.student,
            assignment=self.assignment,
            is_submitted=True
        )
        total = 0
        for answer in answers:
            if answer.selected_choice and answer.selected_choice.is_correct:
                total += answer.question.marks
        self.total_marks_obtained = total
        self.save()
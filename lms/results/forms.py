from django import forms
from django.contrib.auth.models import User
from .models import TrainerUnitAssignment, StudentResult
from courses.models import Unit, Course
from accounts.models import Cohort, StudentProfile

class TrainerUnitAssignmentForm(forms.ModelForm):
    trainer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Trainer"
    )
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all().select_related('course'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Course Unit"
    )
    cohort = forms.ModelChoiceField(
        queryset=Cohort.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Cohort"
    )

    class Meta:
        model = TrainerUnitAssignment
        fields = ['trainer', 'unit', 'cohort']


class StudentResultEntryForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = ['cat_score', 'exam_score', 'is_published', 'verified_by_admin']
        widgets = {
            'cat_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '30'}),
            'exam_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '70'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'verified_by_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class GraduationEligibilityForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['is_eligible_for_graduation', 'graduation_status', 'graduation_notes']
        widgets = {
            'is_eligible_for_graduation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'graduation_status': forms.Select(attrs={'class': 'form-select'}),
            'graduation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional remarks or reasons for eligibility status'}),
        }

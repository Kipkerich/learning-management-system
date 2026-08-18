from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, StudentProfile, Cohort
from finance.models import CourseFee


class BootstrapStyledForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })


class LoginForm(BootstrapStyledForm, AuthenticationForm):
    pass


class AdminUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPES,
        required=True,
        label='User Type'
    )
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "user_type", 
                 "phone_number", "date_of_birth", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.user_type = self.cleaned_data["user_type"]
            user_profile.phone_number = self.cleaned_data["phone_number"]
            user_profile.date_of_birth = self.cleaned_data["date_of_birth"]
            user_profile.save()
            
        return user


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Jan Cohort'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional details about the cohort'}),
        }


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'admission_number', 
            'course', 
            'cohort',
            'enrollment_date',
            'phone_number', 
            'id_number',
            'date_of_birth', 
            'address',
            'gender',
            'marital_status',
            'nationality',
            'former_high_school',
            'parent_primary_name',
            'parent_primary_phone',
            'parent_secondary_name',
            'parent_secondary_phone'
        ]
        
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ADM2026/001'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'cohort': forms.Select(attrs={'class': 'form-select'}),
            'enrollment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +254 700 000000'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 12345678'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. P.O. Box 123, Nairobi'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kenyan'}),
            'former_high_school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Previous High School'}),
            'parent_primary_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary Guardian Name'}),
            'parent_primary_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primary Guardian Phone'}),
            'parent_secondary_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secondary Guardian Name'}),
            'parent_secondary_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secondary Guardian Phone'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = CourseFee.objects.all()
        self.fields['course'].empty_label = "-- Select Available Course --"
        self.fields['cohort'].queryset = Cohort.objects.all()
        self.fields['cohort'].empty_label = "-- Select Cohort --"

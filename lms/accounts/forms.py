from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile , StudentProfile
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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
            # Create or update user profile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.user_type = self.cleaned_data["user_type"]
            user_profile.phone_number = self.cleaned_data["phone_number"]
            user_profile.date_of_birth = self.cleaned_data["date_of_birth"]
            user_profile.save()
            
        return user
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })
        # Make password fields use password input type
        self.fields['password1'].widget.attrs.update({'type': 'password'})
        self.fields['password2'].widget.attrs.update({'type': 'password'})


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

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

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        # Ensure 'course' is in this list!
        fields = [
            'admission_number', 
            'course', 
            'id_number',
            'phone_number', 
            'date_of_birth', 
            'enrollment_date',
            'parent_primary_name', 'parent_primary_phone',
            'parent_secondary_name', 'parent_secondary_phone'
        ]
        
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'enrollment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: You can customize the queryset here if needed
        self.fields['course'].queryset = CourseFee.objects.all()
        self.fields['course'].empty_label = "-- Select Available Course --"
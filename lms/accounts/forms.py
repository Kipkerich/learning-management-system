from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

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
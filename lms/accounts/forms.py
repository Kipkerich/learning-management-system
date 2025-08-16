from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

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
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "is_staff")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show is_staff field to superusers
        if not self.initial.get('is_superuser'):
            self.fields.pop('is_staff')
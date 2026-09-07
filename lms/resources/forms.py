from django import forms
from .models import Resource
from courses.models import Course

class ResourceForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Courses to Publish To",
        error_messages={'required': 'Please select at least one course for this resource.'},
        help_text="Select the course(s) that should have access to this resource."
    )

    class Meta:
        model = Resource
        fields = ['title', 'description', 'resource_type', 'file', 'url', 'courses']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Optional description...'}),
            'resource_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')
        resource_type = cleaned_data.get('resource_type')

        if not file and not url:
            self.add_error('file', "You must provide either a file or a URL.")
            self.add_error('url', "You must provide either a file or a URL.")

        if file and url:
            self.add_error('url', "Please provide either a file or a URL, not both.")

        if resource_type in ['document', 'video'] and not file:
            self.add_error('file', f"A file upload is required for {resource_type} resources.")

        if resource_type == 'link' and not url:
            self.add_error('url', "A URL is required for link resources.")

        return cleaned_data

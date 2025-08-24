from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'resource_type', 'file', 'url', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')

        if not file and not url:
            raise forms.ValidationError("You must provide either a file or a URL.")
        
        if file and url:
            raise forms.ValidationError("Please provide either a file or a URL, not both.")
        
        return cleaned_data
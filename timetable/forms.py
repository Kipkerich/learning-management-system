from django import forms
from .models import Timetable
from datetime import timedelta

class TimetableForm(forms.ModelForm):
    repeat_count = forms.IntegerField(
        required=False,
        min_value=1,
        help_text="Repeat weekly for X weeks. Leave empty for no repeat."
    )

    class Meta:
        model = Timetable
        fields = [
            'course', 'date', 'start_time', 'end_time', 
            'subject', 'trainer', 'location', 'description', 
            'repeat_count', 'is_published'
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),          
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        if date and start_time and end_time:
            conflicts = Timetable.objects.filter(date=date).exclude(pk=self.instance.pk)
            for session in conflicts:
                if (start_time < session.end_time and end_time > session.start_time):
                    raise forms.ValidationError(
                        f"Time conflict with {session.subject} ({session.start_time}-{session.end_time})"
                    )

        return cleaned_data

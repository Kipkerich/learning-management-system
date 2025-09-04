from django import forms
from .models import Timetable

class TimetableForm(forms.ModelForm):
    extra_dates = forms.CharField(
        required=False,
        help_text="Enter extra dates separated by commas (YYYY-MM-DD, YYYY-MM-DD, ...)"
    )

    class Meta:
        model = Timetable
        fields = ['date', 'start_time', 'end_time', 'subject', 'trainer', 'location', 'description', 'is_published']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
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

        # prevent conflicts
        if date and start_time and end_time:
            conflicts = Timetable.objects.filter(date=date).exclude(pk=self.instance.pk)
            for session in conflicts:
                if (start_time < session.end_time and end_time > session.start_time):
                    raise forms.ValidationError(
                        f"Time conflict with {session.subject} ({session.start_time}-{session.end_time})"
                    )

        return cleaned_data


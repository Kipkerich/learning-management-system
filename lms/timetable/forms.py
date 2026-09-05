from django import forms
from django.contrib.auth.models import User
from .models import Timetable, Room
from courses.models import Course, Unit

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TimetableForm(forms.ModelForm):
    repeat_count = forms.IntegerField(
        required=False,
        min_value=1,
        help_text="Repeat weekly for X weeks. Leave empty for no repeat."
    )

    class Meta:
        model = Timetable
        fields = [
            'course', 'unit', 'unit_type', 'date', 'start_time', 'end_time',
            'subject', 'trainer', 'location', 'description', 
            'repeat_count', 'is_published'
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select', 'id': 'id_course'}),
            'unit': forms.Select(attrs={'class': 'form-select', 'id': 'id_unit'}),
            'unit_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_unit_type'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),          
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'trainer': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()
        self.fields['course'].empty_label = "-- Select Course --"
        self.fields['unit'].queryset = Unit.objects.none()
        self.fields['unit'].empty_label = "-- Select Unit --"
        self.fields['trainer'].queryset = User.objects.filter(userprofile__user_type='trainer')
        self.fields['trainer'].empty_label = "-- Select Trainer --"
        self.fields['location'].queryset = Room.objects.all()
        self.fields['location'].empty_label = "-- Select Location/Room --"
        self.fields['subject'].required = False

        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                self.fields['unit'].queryset = Unit.objects.filter(course_id=course_id)
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.pk and self.instance.course:
            self.fields['unit'].queryset = self.instance.course.units.all()

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        trainer = cleaned_data.get('trainer')
        location = cleaned_data.get('location')
        unit = cleaned_data.get('unit')
        unit_type = cleaned_data.get('unit_type') or 'core'

        if unit and not cleaned_data.get('subject'):
            cleaned_data['subject'] = unit.name

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")

        if date and start_time and end_time:
            # Check trainer double-booking
            if trainer:
                trainer_conflicts = Timetable.objects.filter(
                    date=date,
                    trainer=trainer
                ).exclude(pk=self.instance.pk)
                for session in trainer_conflicts:
                    if start_time < session.end_time and end_time > session.start_time:
                        is_combined_common = (
                            unit_type == 'common' and
                            session.unit_type == 'common' and
                            location and
                            session.location == location
                        )
                        if not is_combined_common:
                            raise forms.ValidationError(
                                f"Trainer {trainer.get_full_name() or trainer.username} is already assigned to a class at this time ({session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')})."
                            )

            # Check room double-booking
            if location:
                room_conflicts = Timetable.objects.filter(
                    date=date,
                    location=location
                ).exclude(pk=self.instance.pk)
                for session in room_conflicts:
                    if start_time < session.end_time and end_time > session.start_time:
                        is_combined_common = (
                            unit_type == 'common' and
                            session.unit_type == 'common' and
                            trainer and
                            session.trainer == trainer
                        )
                        if not is_combined_common:
                            raise forms.ValidationError(
                                f"Room '{location.name}' is already reserved for another unit at this time ({session.start_time.strftime('%H:%M')}-{session.end_time.strftime('%H:%M')})."
                            )

        return cleaned_data

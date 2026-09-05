from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Unit


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


UNIT_TYPE_CHOICES = [
    ('core', 'Core Unit'),
    ('common', 'Common Unit'),
]


class Timetable(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=100, blank=True)
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timetable_sessions'
    )
    location = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_sessions'
    )
    unit_type = models.CharField(
        max_length=10,
        choices=UNIT_TYPE_CHOICES,
        default='core',
        verbose_name="Unit Type"
    )
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE, 
        related_name='timetable_entries',
        null=True,
        blank=True
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        subj = self.unit.name if self.unit else self.subject
        return f"{self.date} - {subj} ({self.start_time} to {self.end_time})"

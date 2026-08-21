from django.db import models
from django.contrib.auth.models import User
from finance.models import CourseFee

class Timetable(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=100)
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timetable_sessions'
    )
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(
        CourseFee, 
        on_delete=models.CASCADE, 
        related_name='timetable_entries',
        null=True,  # Allows existing entries to remain valid
        blank=False # Makes it mandatory for new entries
    )
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['date', 'start_time', 'trainer']

    def __str__(self):
        return f"{self.date} - {self.subject} ({self.start_time} to {self.end_time})"

from django.db import models
from django.contrib.auth.models import User

class Timetable(models.Model):
    DAYS_OF_WEEK = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    )

    date = models.DateField(null=True, blank=True)  # Optional exact date
    day = models.CharField(
        max_length=10,
        choices=DAYS_OF_WEEK,
        default='monday'
    )
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

    class Meta:
        ordering = ['day', 'start_time']
        unique_together = ['day', 'start_time', 'trainer']

    def __str__(self):
        return f"{self.day} - {self.subject} ({self.start_time} to {self.end_time})"

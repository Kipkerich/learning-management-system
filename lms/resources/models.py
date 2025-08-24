# resources/models.py
from django.db import models
from django.contrib.auth.models import User
import os

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('document', 'Document'),
        ('video', 'Video'),
        ('link', 'Link'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES, default='document')
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    url = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        return None

    def get_absolute_url(self):
        return f"/resources/{self.id}/"
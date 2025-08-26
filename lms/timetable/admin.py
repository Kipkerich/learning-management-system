from django.contrib import admin
from .models import Timetable

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time', 'subject', 'trainer', 'location', 'is_published']
    list_filter = ['day', 'is_published', 'trainer']
    search_fields = ['subject', 'trainer__username', 'location']
    list_editable = ['is_published']
from django.contrib import admin
from .models import Timetable

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('day', 'date', 'start_time', 'end_time', 'subject', 'trainer', 'is_published')
    list_filter = ('day', 'date', 'trainer', 'is_published')
    search_fields = ('subject', 'trainer__username', 'location')
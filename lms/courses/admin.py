from django.contrib import admin
from .models import Course, Unit

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'school_fee', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'course', 'created_at')
    search_fields = ('name', 'code', 'course__name')
    list_filter = ('course',)

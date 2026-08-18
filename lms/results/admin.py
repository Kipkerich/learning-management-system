from django.contrib import admin
from .models import TrainerUnitAssignment, StudentResult

@admin.register(TrainerUnitAssignment)
class TrainerUnitAssignmentAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'unit', 'cohort', 'assigned_at')
    list_filter = ('cohort', 'unit__course')
    search_fields = ('trainer__username', 'trainer__first_name', 'unit__name', 'unit__code')


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit', 'cohort', 'cat_score', 'exam_score', 'total_score', 'grade', 'is_published', 'verified_by_admin')
    list_filter = ('is_published', 'verified_by_admin', 'cohort', 'unit__course')
    search_fields = ('student__admission_number', 'student__user__username', 'unit__name', 'unit__code')

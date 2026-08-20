from django.db import models
from django.contrib.auth.models import User
from courses.models import Unit
from accounts.models import Cohort, StudentProfile

class TrainerUnitAssignment(models.Model):
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unit_assignments')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='trainer_assignments')
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='trainer_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trainer', 'unit', 'cohort')

    def __str__(self):
        return f"{self.trainer.get_full_name() or self.trainer.username} - {self.unit.code} ({self.cohort.name})"


class StudentResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='results')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='student_results')
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='student_results')
    cat_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="CAT Score (Out of 30)")
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Exam Score (Out of 70)")
    is_published = models.BooleanField(default=False)
    verified_by_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'unit')

    def __str__(self):
        return f"{self.student.admission_number} - {self.unit.code}: Total {self.total_score}"

    @property
    def total_score(self):
        return (self.cat_score or 0) + (self.exam_score or 0)

    @property
    def grade(self):
        total = self.total_score
        if total >= 70:
            return 'A'
        elif total >= 60:
            return 'B'
        elif total >= 50:
            return 'C'
        elif total >= 40:
            return 'D'
        else:
            return 'E'

    @property
    def remarks(self):
        return 'PASS' if self.total_score >= 40 else 'FAIL'

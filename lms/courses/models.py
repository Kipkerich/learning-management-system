from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Course(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Course Name")
    code = models.CharField(max_length=50, unique=True, verbose_name="Course Code")
    description = models.TextField(blank=True, verbose_name="Description")
    school_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="School Fee (KES)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Unit(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=200, verbose_name="Unit Name")
    code = models.CharField(max_length=50, verbose_name="Unit Code")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'code')

    def __str__(self):
        return f"{self.code}: {self.name}"


@receiver(post_save, sender=Course)
def sync_course_fee_on_save(sender, instance, created, **kwargs):
    from finance.models import CourseFee
    CourseFee.objects.update_or_create(
        course_name=instance.name,
        defaults={
            'total_amount': instance.school_fee,
            'description': instance.description or f"Fee for {instance.name}"
        }
    )


@receiver(post_delete, sender=Course)
def sync_course_fee_on_delete(sender, instance, **kwargs):
    from finance.models import CourseFee
    CourseFee.objects.filter(course_name=instance.name).delete()

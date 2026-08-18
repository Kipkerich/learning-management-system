from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone


class UserProfile(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('trainer', 'Trainer'),
        ('admin', 'Administrator'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Cohort(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Cohort Name")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    former_high_school = models.CharField(max_length=200, blank=True)
    course = models.ForeignKey('finance.CourseFee', on_delete=models.SET_NULL, null=True, blank=True)
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=[
        ('Single', 'Single'), 
        ('Married', 'Married'), 
        ('Other', 'Other')
    ], default='Single')
    nationality = models.CharField(max_length=100, default='Kenyan')
    id_number = models.IntegerField(unique=True, null=True, blank=True, verbose_name="ID Number")
    enrollment_date = models.DateField(default=timezone.now)
    parent_primary_name = models.CharField(max_length=200, blank=True, null=True)
    parent_primary_phone = models.CharField(max_length=20, blank=True, null=True)
    parent_secondary_name = models.CharField(max_length=200, blank=True, null=True)
    parent_secondary_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Financial Link
    is_fully_paid = models.BooleanField(default=False)

    # Graduation Eligibility Fields
    is_eligible_for_graduation = models.BooleanField(default=False)
    graduation_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending Review'),
        ('Eligible', 'Eligible for Graduation'),
        ('Not Eligible', 'Not Eligible'),
        ('Graduated', 'Graduated')
    ], default='Pending')
    graduation_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"

    # --- Finance Logic ---
    @property
    def total_invoiced(self):
        """Calculates total amount this student has been billed."""
        return self.invoices.aggregate(Sum('fee_type__amount'))['fee_type__amount__sum'] or 0

    @property
    def total_paid(self):
        """Calculates total amount this student has actually paid."""
        from finance.models import Payment
        return Payment.objects.filter(invoice__student=self).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    @property
    def balance(self):
        """The remaining amount the student owes."""
        return self.total_invoiced - self.total_paid

    @property
    def is_fully_paid(self):
        """Used by template badges to show 'Cleared' or 'Balance'."""
        return self.balance <= 0

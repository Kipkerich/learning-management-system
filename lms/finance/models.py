from django.db import models
from accounts.models import StudentProfile

class CourseFee(models.Model):
    """The 'Price List' for courses."""
    course_name = models.CharField(max_length=100, unique=True) # e.g., "Diploma in IT"
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course_name} (KES {self.total_amount})"

class FeeStructure(models.Model):
    """Defines the standard fees for different categories (e.g., Tuition, Lab, Library)"""
    name = models.CharField(max_length=100) # e.g., "Year 1 Tuition"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __clstr__(self):
        return f"{self.name} - KES {self.amount}"

class Invoice(models.Model):
    """The bill issued to a specific student"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='invoices')
    fee_type = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)
    issued_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice for {self.student.admission_number} - {self.fee_type.name}"

class Payment(models.Model):
    """The actual money received from a student"""
    PAYMENT_METHODS = [
        ('Mpesa', 'Mpesa'),
        ('Bank', 'Bank Deposit'),
        ('Cash', 'Cash'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=50, unique=True) # Receipt No. or Mpesa ID
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    date_paid = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount_paid}"
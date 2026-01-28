from django import forms
from .models import CourseFee, Payment

class CourseFeeForm(forms.ModelForm):
    """
    Used in the Finance Hub to let the officer 
    create or update the cost of a specific course.
    """
    class Meta:
        model = CourseFee
        fields = ['course_name', 'total_amount', 'description']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Diploma in Computer Science'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter total fee (e.g., 50000)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Optional details about the course'
            }),
        }

class PaymentForm(forms.ModelForm):
    """
    Used to record money received from a student.
    """
    class Meta:
        model = Payment
        fields = ['amount_paid', 'transaction_id', 'payment_method']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'KES 0.00'
            }),
            'transaction_id': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Mpesa ID / Bank Ref'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Optional: accept 'invoice' to validate against overpayment
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
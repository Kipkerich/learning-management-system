from django import forms
from .models import CourseFee, Payment
from courses.models import Course

class CourseFeeForm(forms.ModelForm):
    """
    Used in the Finance Hub to let the officer 
    add or update the school fee of an available course.
    """
    available_course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        label="Select Available Course",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select a course from the offered courses, or enter a course name manually."
    )

    class Meta:
        model = CourseFee
        fields = ['available_course', 'course_name', 'total_amount', 'description']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Or enter course name manually'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter school fee (e.g., 50000)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Optional details about the fee structure'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course_name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        available_course = cleaned_data.get('available_course')
        course_name = cleaned_data.get('course_name')

        if available_course:
            cleaned_data['course_name'] = available_course.name
        elif not course_name:
            raise forms.ValidationError("Please select an available course or enter a course name manually.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        available_course = self.cleaned_data.get('available_course')
        if available_course:
            instance.course_name = available_course.name
            available_course.school_fee = instance.total_amount
            available_course.save()
        else:
            course_obj = Course.objects.filter(name__iexact=instance.course_name).first()
            if course_obj:
                course_obj.school_fee = instance.total_amount
                course_obj.save()

        if commit:
            instance.save()
        return instance

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
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)

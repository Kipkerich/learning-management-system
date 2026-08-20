from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum
from .models import CourseFee, Payment, Invoice
from .forms import CourseFeeForm, PaymentForm
from accounts.models import StudentProfile

@staff_member_required
def finance_index(request):
    """
    Dashboard for Finance Officer to manage Course Fees 
    and view all student balances.
    """
    if request.method == 'POST':
        # Logic for adding a new Course Fee structure
        form = CourseFeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Course Fee structure added.")
            return redirect('finance_index')

    # Data for the hub
    courses = CourseFee.objects.all()
    students = StudentProfile.objects.all().select_related('user', 'course')
    
    # Calculate total collections across the whole school
    total_collected = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    return render(request, 'finance/index.html', {
        'courses': courses,
        'students': students,
        'form': CourseFeeForm(),
        'total_collected': total_collected
    })
    
    
@staff_member_required
def record_payment(request, invoice_id):
    """
    Records a transaction against a student's invoice.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    student = invoice.student

    if request.method == 'POST':
        form = PaymentForm(request.POST, invoice=invoice)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()
            
            # Check if invoice is fully settled
            total_paid = invoice.payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            if total_paid >= invoice.amount: # assuming 'amount' is stored on Invoice
                invoice.is_paid = True
                invoice.save()

            messages.success(request, f"Payment of {payment.amount_paid} received for {student.user.get_full_name()}")
            return redirect('student_detail', pk=student.pk)
    else:
        form = PaymentForm(invoice=invoice)

    return render(request, 'finance/record_payment.html', {
        'form': form,
        'invoice': invoice,
        'student': student
    })
    
# Update Course
@staff_member_required
def edit_course(request, pk):
    course = get_object_or_404(CourseFee, pk=pk)
    if request.method == 'POST':
        form = CourseFeeForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.info(request, "Course updated successfully.")
            return redirect('finance_index')
    else:
        form = CourseFeeForm(instance=course)
    return render(request, 'finance/edit_course.html', {'form': form, 'course': course})

# Delete Course
@staff_member_required
def delete_course(request, pk):
    course = get_object_or_404(CourseFee, pk=pk)
    course.delete()
    messages.warning(request, "Course fee structure removed.")
    return redirect('finance_index')
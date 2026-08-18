# timetable/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Timetable
from .forms import TimetableForm
from datetime import datetime, timedelta
from django.db.models import DateField
from django.db.models.functions import TruncDate
from django.db import transaction
from collections import defaultdict
from finance.models import CourseFee


def is_admin(user):
    return user.is_superuser

def is_trainer(user):
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'trainer'

def is_student(user):
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'student'

@login_required
def timetable_view(request):
    selected_course = request.GET.get('course')
    
    # Base Queryset
    if is_admin(request.user):
        timetables = Timetable.objects.all()
    else:
        timetables = Timetable.objects.filter(is_published=True)

    # Apply Filter if a course is selected
    if selected_course:
        timetables = timetables.filter(course_id=selected_course)

    # Order and Group as before
    timetables = timetables.order_by('date', 'start_time')
    dates_dict = defaultdict(list)
    for session in timetables:
        dates_dict[session.date].append(session)

    sorted_dates = sorted(dates_dict.items())

    context = {
        'dates': sorted_dates,
        'is_admin': is_admin(request.user),
        'courses': CourseFee.objects.all(), # Pass all courses for the dropdown
        'selected_course': selected_course,
    }
    return render(request, 'timetable/timetable.html', context)

@login_required
@user_passes_test(is_admin)
def create_timetable(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. EXTRACT DATA FIRST
                    repeat_count = form.cleaned_data.get('repeat_count') or 1
                    base_date = form.cleaned_data['date']
                    start_time = form.cleaned_data['start_time']  # <--- Added this
                    end_time = form.cleaned_data['end_time']      # <--- Added this
                    subject = form.cleaned_data['subject']
                    trainer = form.cleaned_data['trainer']
                    location = form.cleaned_data['location']
                    description = form.cleaned_data['description']
                    is_published = form.cleaned_data['is_published']

                    # 2. NOW START THE LOOP
                    for i in range(repeat_count):
                        schedule_date = base_date + timedelta(days=7 * i)

                        # Conflict check
                        conflicts = Timetable.objects.filter(date=schedule_date)
                        for session in conflicts:
                            if (start_time < session.end_time and end_time > session.start_time):
                                messages.error(request, f"Conflict on {schedule_date} with {session.subject}. No entries saved.")
                                return render(request, 'timetable/create_timetable.html', {'form': form})

                        # Save the entry
                        Timetable.objects.create(
                            date=schedule_date,
                            start_time=start_time,
                            end_time=end_time,
                            subject=subject,
                            trainer=trainer,
                            location=location,
                            description=description,
                            is_published=is_published,
                        )

                messages.success(request, f'Successfully created {repeat_count} weekly entries!')
                return redirect('timetable')

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
    else:
        form = TimetableForm()

    return render(request, 'timetable/create_timetable.html', {'form': form})
@login_required
@user_passes_test(is_admin)
def edit_timetable(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    
    if request.method == 'POST':
        form = TimetableForm(request.POST, instance=timetable)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry updated successfully!')
            return redirect('timetable')
    else:
        form = TimetableForm(instance=timetable)
    
    context = {'form': form, 'timetable': timetable}
    return render(request, 'timetable/edit_timetable.html', context)

@login_required
@user_passes_test(is_admin)
def delete_timetable(request, pk):
    timetable = get_object_or_404(Timetable, pk=pk)
    
    if request.method == 'POST':
        timetable.delete()
        messages.success(request, 'Timetable entry deleted successfully!')
        return redirect('timetable')
    
    context = {'timetable': timetable}
    return render(request, 'timetable/delete_timetable.html', context)

# API endpoint for calendar view
@login_required
def timetable_json(request):
    timetables = Timetable.objects.filter(is_published=True)
    data = []

    for timetable in timetables:
        data.append({
            'title': f"{timetable.subject} - {timetable.trainer.get_full_name()}",
            'start': f"{timetable.date}T{timetable.start_time}",
            'end': f"{timetable.date}T{timetable.end_time}",
            'location': timetable.location,
            'description': timetable.description,
        })

    return JsonResponse(data, safe=False)

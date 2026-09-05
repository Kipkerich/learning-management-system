# timetable/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Timetable, Room
from .forms import TimetableForm, RoomForm
from datetime import datetime, timedelta
from django.db import transaction
from collections import defaultdict
from courses.models import Course, Unit


def is_admin(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin')

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
    elif is_student(request.user) and hasattr(request.user, 'student_profile') and request.user.student_profile.course:
        timetables = Timetable.objects.filter(is_published=True, course=request.user.student_profile.course)
    else:
        timetables = Timetable.objects.filter(is_published=True)

    # Apply Filter if a course is selected
    if selected_course:
        timetables = timetables.filter(course_id=selected_course)

    # Order and Group
    timetables = timetables.order_by('date', 'start_time')
    dates_dict = defaultdict(list)
    for session in timetables:
        dates_dict[session.date].append(session)

    sorted_dates = sorted(dates_dict.items())

    context = {
        'dates': sorted_dates,
        'is_admin': is_admin(request.user),
        'courses': Course.objects.all(), # Pass all courses for the dropdown
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
                    repeat_count = form.cleaned_data.get('repeat_count') or 1
                    base_date = form.cleaned_data['date']
                    start_time = form.cleaned_data['start_time']
                    end_time = form.cleaned_data['end_time']
                    course = form.cleaned_data['course']
                    unit = form.cleaned_data['unit']
                    unit_type = form.cleaned_data.get('unit_type') or 'core'
                    subject = form.cleaned_data.get('subject') or (unit.name if unit else '')
                    trainer = form.cleaned_data['trainer']
                    location = form.cleaned_data['location']
                    description = form.cleaned_data['description']
                    is_published = form.cleaned_data['is_published']

                    # Loop for repeating weeks
                    for i in range(repeat_count):
                        schedule_date = base_date + timedelta(days=7 * i)

                        # Check trainer conflict
                        trainer_conflicts = Timetable.objects.filter(
                            date=schedule_date,
                            trainer=trainer
                        )
                        for session in trainer_conflicts:
                            if start_time < session.end_time and end_time > session.start_time:
                                is_combined_common = (
                                    unit_type == 'common' and
                                    session.unit_type == 'common' and
                                    location and
                                    session.location == location
                                )
                                if not is_combined_common:
                                    messages.error(request, f"Conflict on {schedule_date}: Trainer {trainer.get_full_name() or trainer.username} is already assigned at this time. No entries saved.")
                                    return render(request, 'timetable/create_timetable.html', {'form': form})

                        # Check room conflict
                        if location:
                            room_conflicts = Timetable.objects.filter(
                                date=schedule_date,
                                location=location
                            )
                            for session in room_conflicts:
                                if start_time < session.end_time and end_time > session.start_time:
                                    is_combined_common = (
                                        unit_type == 'common' and
                                        session.unit_type == 'common' and
                                        trainer and
                                        session.trainer == trainer
                                    )
                                    if not is_combined_common:
                                        messages.error(request, f"Conflict on {schedule_date}: Room '{location.name}' is already booked at this time. No entries saved.")
                                        return render(request, 'timetable/create_timetable.html', {'form': form})

                        # Create entry
                        Timetable.objects.create(
                            date=schedule_date,
                            start_time=start_time,
                            end_time=end_time,
                            course=course,
                            unit=unit,
                            unit_type=unit_type,
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
    if is_admin(request.user):
        timetables = Timetable.objects.all()
    elif is_student(request.user) and hasattr(request.user, 'student_profile') and request.user.student_profile.course:
        timetables = Timetable.objects.filter(is_published=True, course=request.user.student_profile.course)
    else:
        timetables = Timetable.objects.filter(is_published=True)

    data = []

    for timetable in timetables:
        data.append({
            'title': f"{timetable.unit.name if timetable.unit else timetable.subject} - {timetable.trainer.get_full_name() or timetable.trainer.username}",
            'start': f"{timetable.date}T{timetable.start_time}",
            'end': f"{timetable.date}T{timetable.end_time}",
            'location': timetable.location.name if timetable.location else '',
            'description': timetable.description,
        })

    return JsonResponse(data, safe=False)

# API endpoint for dynamic units dropdown based on course
@login_required
def get_units_by_course(request):
    course_id = request.GET.get('course_id')
    units_data = []
    if course_id:
        units = Unit.objects.filter(course_id=course_id)
        for u in units:
            units_data.append({'id': u.id, 'name': f"{u.code}: {u.name}"})
    return JsonResponse({'units': units_data})

# Room Management Views
@login_required
@user_passes_test(is_admin)
def manage_rooms(request):
    rooms = Room.objects.all()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Room added successfully!")
            return redirect('manage_rooms')
    else:
        form = RoomForm()
    return render(request, 'timetable/manage_rooms.html', {'rooms': rooms, 'form': form})

@login_required
@user_passes_test(is_admin)
def edit_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully!")
            return redirect('manage_rooms')
    else:
        form = RoomForm(instance=room)
    return render(request, 'timetable/edit_room.html', {'form': form, 'room': room})

@login_required
@user_passes_test(is_admin)
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, "Room deleted successfully!")
        return redirect('manage_rooms')
    return render(request, 'timetable/delete_room.html', {'room': room})

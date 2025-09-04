# timetable/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Timetable
from .forms import TimetableForm
from datetime import timedelta
from django.utils import timezone

def is_admin(user):
    return user.is_superuser

def is_trainer(user):
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'trainer'

def is_student(user):
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'student'

@login_required
def timetable_view(request):
    # Only show published timetables to non-admins
    if is_admin(request.user):
        timetables = Timetable.objects.all()
    else:
        timetables = Timetable.objects.filter(is_published=True)
    
    # Group by day for easier display
    days = {
        'monday': [],
        'tuesday': [],
        'wednesday': [],
        'thursday': [],
        'friday': [],
 
    }
    
    for timetable in timetables:
        days[timetable.day].append(timetable)
    
    context = {
        'days': days,
        'is_admin': is_admin(request.user),
        'is_trainer': is_trainer(request.user),
        'is_student': is_student(request.user),
    }
    return render(request, 'timetable/timetable.html', context)

@login_required
@user_passes_test(is_admin)
def create_timetable(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            timetable = form.save()

            # Handle multiple extra dates
            extra_dates_str = form.cleaned_data.get('extra_dates', '')
            if extra_dates_str:
                extra_dates = [d.strip() for d in extra_dates_str.split(',')]
                for d in extra_dates:
                    try:
                        parsed_date = datetime.strptime(d, "%Y-%m-%d").date()
                        Timetable.objects.create(
                            date=parsed_date,
                            start_time=timetable.start_time,
                            end_time=timetable.end_time,
                            subject=timetable.subject,
                            trainer=timetable.trainer,
                            location=timetable.location,
                            description=timetable.description,
                            is_published=timetable.is_published,
                        )
                    except ValueError:
                        continue  # skip invalid dates

            messages.success(request, 'Timetable entry (and extra dates) created successfully!')
            return redirect('timetable')
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

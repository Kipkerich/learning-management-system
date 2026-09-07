from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm


def can_manage_resources(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return hasattr(user, 'userprofile') and user.userprofile.user_type in ['trainer', 'admin']


def is_trainer(user):
    return can_manage_resources(user)


@login_required
def resources_view(request):
    can_manage = can_manage_resources(request.user)
    if can_manage:
        resources = Resource.objects.all().distinct()
    else:
        if hasattr(request.user, 'student_profile') and request.user.student_profile and request.user.student_profile.course:
            resources = Resource.objects.filter(courses=request.user.student_profile.course).distinct()
        else:
            resources = Resource.objects.none()

    return render(request, 'resources/resources.html', {
        'resources': resources,
        'is_trainer': can_manage,
        'can_manage': can_manage,
    })


@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    can_manage = can_manage_resources(request.user)

    if not can_manage:
        if hasattr(request.user, 'student_profile') and request.user.student_profile and request.user.student_profile.course:
            if not resource.courses.filter(pk=request.user.student_profile.course.pk).exists():
                raise Http404("Resource not found")
        else:
            raise Http404("Resource not found")

    return render(request, 'resources/resource_detail.html', {
        'resource': resource,
        'is_trainer': can_manage,
        'can_manage': can_manage,
    })


@login_required
def download_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    can_manage = can_manage_resources(request.user)

    if not can_manage:
        if hasattr(request.user, 'student_profile') and request.user.student_profile and request.user.student_profile.course:
            if not resource.courses.filter(pk=request.user.student_profile.course.pk).exists():
                raise Http404("Resource not found")
        else:
            raise Http404("Resource not found")

    if resource.file:
        response = FileResponse(resource.file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{resource.filename()}"'
        return response

    messages.error(request, "No file available for download.")
    return redirect('resources')


@login_required
def add_resource(request):
    if not can_manage_resources(request.user):
        messages.error(request, "Only trainers and admins can add resources.")
        return redirect('resources')

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            form.save_m2m()
            messages.success(request, 'Resource added successfully!')
            return redirect('resources')
    else:
        form = ResourceForm()

    return render(request, 'resources/add_resource.html', {'form': form})


@login_required
def edit_resource(request, pk):
    if not can_manage_resources(request.user):
        messages.error(request, "Only trainers and admins can edit resources.")
        return redirect('resources')

    if request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'admin'):
        resource = get_object_or_404(Resource, pk=pk)
    else:
        resource = get_object_or_404(Resource, pk=pk, uploaded_by=request.user)

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('resource_detail', pk=resource.pk)
    else:
        form = ResourceForm(instance=resource)

    return render(request, 'resources/edit_resource.html', {
        'form': form,
        'resource': resource
    })


@login_required
def delete_resource(request, pk):
    if not can_manage_resources(request.user):
        messages.error(request, "Only trainers and admins can delete resources.")
        return redirect('resources')

    if request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'admin'):
        resource = get_object_or_404(Resource, pk=pk)
    else:
        resource = get_object_or_404(Resource, pk=pk, uploaded_by=request.user)

    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully!')
        return redirect('resources')

    return render(request, 'resources/delete_resource.html', {'resource': resource})

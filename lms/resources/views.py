from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm

def is_trainer(user):
    return hasattr(user, 'userprofile') and user.userprofile.user_type == 'trainer'

@login_required
def resources_view(request):
    resources = Resource.objects.filter(is_published=True)
    
    # Trainers can see all resources, students see only published ones
    if is_trainer(request.user):
        resources = Resource.objects.all()
    
    context = {
        'resources': resources,
        'is_trainer': is_trainer(request.user)
    }
    return render(request, 'resources/resources.html', context)

@login_required
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    
    # Check if resource is published or user is trainer
    if not resource.is_published and not is_trainer(request.user):
        raise Http404("Resource not found")
    
    context = {
        'resource': resource,
        'is_trainer': is_trainer(request.user)
    }
    return render(request, 'resources/resource_detail.html', context)

@login_required
def download_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    
    if resource.file:
        response = FileResponse(resource.file.open(), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{resource.filename()}"'
        return response
    else:
        raise Http404("No file available for download")

@login_required
def add_resource(request):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can add resources.")
        return redirect('resources')
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, 'Resource added successfully!')
            return redirect('resources')
    else:
        form = ResourceForm()
    
    context = {'form': form}
    return render(request, 'resources/add_resource.html', context)

@login_required
def edit_resource(request, pk):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can edit resources.")
        return redirect('resources')
    
    resource = get_object_or_404(Resource, pk=pk, uploaded_by=request.user)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('resource_detail', pk=resource.pk)
    else:
        form = ResourceForm(instance=resource)
    
    context = {'form': form, 'resource': resource}
    return render(request, 'resources/edit_resource.html', context)

@login_required
def delete_resource(request, pk):
    if not is_trainer(request.user):
        messages.error(request, "Only trainers can delete resources.")
        return redirect('resources')
    
    resource = get_object_or_404(Resource, pk=pk, uploaded_by=request.user)
    
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully!')
        return redirect('resources')
    
    context = {'resource': resource}
    return render(request, 'resources/delete_resource.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lab
from .forms import LabForm
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

@login_required(login_url='login')
def lab_list(request):
    query = request.GET.get('q', '').strip()

    # Get all labs sorted by newest first
    labs = Lab.objects.filter(status='Active').order_by('-created_date')

    # Optional search functionality
    if query:
        labs = labs.filter(
            Q(lab_name__icontains=query) |
            Q(lab_id__icontains=query) |
            Q(email__icontains=query) |
            Q(contact_no__icontains=query) 
        )

    # Pagination
    paginator = Paginator(labs, 5)  # Show 5 labs per page
    page_number = request.GET.get('page')
    labs_page = paginator.get_page(page_number)

    return render(request, 'labs/lab_list.html', {
        'labs': labs_page,
        'query': query,
    })


# ------------------------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def lab_create(request):
    print("lab_create view called")
    if request.method == 'POST':
        print("POST data received:", request.POST)
        form = LabForm(request.POST)
        print("Form instance created:", form)
        print("Form is valid:", form.is_valid())
        print("Form errors:", form.errors)
        if form.is_valid():
            form.save()
            return redirect('lab_list')
    else:
        form = LabForm()
    return render(request, 'labs/lab_form.html', {'form': form, 'title': 'Add Lab'})


@login_required(login_url='login')
def lab_update(request, pk):
    lab = get_object_or_404(Lab, pk=pk)

    if request.method == 'POST':
        form = LabForm(request.POST, instance=lab)
        if form.is_valid():
            form.save()
            return redirect('lab_list')
    else:
        form = LabForm(instance=lab)

    return render(request, 'labs/lab_edit.html', {'form': form, 'lab': lab})


@login_required(login_url='login')
def lab_delete(request, pk):
    lab = get_object_or_404(Lab, pk=pk)
    if request.method == 'POST':
        lab.status = 'Inactive'
        lab.save()
        return redirect('lab_list')
    return render(request, 'labs/lab_confirm_delete.html', {'lab': lab})



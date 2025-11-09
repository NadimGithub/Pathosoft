import re
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Lab
from .forms import LabForm

logger = logging.getLogger('pathosoft')

# ----------------------------------------------------------------------------------------
@login_required(login_url='login')
def lab_list(request):
    try:
        logger.info(f"Accessing lab list - User: {request.user.username}")
        query = request.GET.get('q', '').strip()

        labs = Lab.objects.filter(status='Active').order_by('-created_date')

        if query:
            logger.debug(f"Searching labs with query: {query}")
            labs = labs.filter(
                Q(lab_name__icontains=query) |
                Q(lab_id__icontains=query) |
                Q(email__icontains=query) |
                Q(contact_no__icontains=query)
            )

        logger.debug(f"Found {labs.count()} labs matching criteria")
        return render(request, 'labs/lab_list.html', {
            'labs': labs,
            'query': query,
        })
    except Exception as e:
        logger.error(f"Error fetching lab list: {str(e)}", exc_info=True)
        messages.error(request, "Error fetching lab list. Please try again.")
        return redirect('login')
# ----------------------------------------------------------------------------------------


@login_required(login_url='login')
def lab_create(request):
    try:
        logger.info(f"Creating new lab - User: {request.user.username}")

        if request.method == 'POST':
            form = LabForm(request.POST)
            lab_name = request.POST.get("lab_name", "").strip()
            address = request.POST.get("address", "").strip()
            email = request.POST.get("email", "").strip()
            contact_no = request.POST.get("contact_no", "").strip()

            # --- Backend Validations ---
            has_error = False

            # 1️⃣ Required fields check
            if not lab_name or not address or not email or not contact_no:
                messages.error(request, "All fields are required.")
                has_error = True

            # 2️⃣ Contact number validation (10 digits only, starting 6–9)
            elif not re.fullmatch(r"^[6-9]\d{9}$", contact_no):
                messages.error(request, "Enter a valid 10-digit contact number starting with 6–9.")
                has_error = True

            # 3️⃣ Email format validation
            elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, "Enter a valid email address.")
                has_error = True

            # 4️⃣ Duplicate check for name or email
            elif Lab.objects.filter(Q(lab_name__iexact=lab_name) | Q(email__iexact=email), status="Active").exists():
                messages.error(request, "A lab with this name or email already exists.")
                has_error = True

            # Return back with error messages
            if has_error:
                logger.warning(f"Lab creation validation failed for {lab_name}")
                return render(request, 'labs/lab_form.html', {'form': form, 'title': 'Add Lab'})

            # ✅ If all validations pass, save
            if form.is_valid():
                lab = form.save(commit=False)
                lab.status = "Active"
                lab.save()
                logger.info(f"Lab created successfully - ID: {lab.lab_id}")
                messages.success(request, f"Lab '{lab.lab_name}' created successfully!")
                return redirect('lab_list')
            else:
                messages.error(request, "Form contains invalid data.")
        else:
            form = LabForm()

    except Exception as e:
        logger.error(f"Error creating lab: {str(e)}", exc_info=True)
        messages.error(request, "An unexpected error occurred while creating the lab.")
        return redirect('lab_list')

    return render(request, 'labs/lab_form.html', {'form': form, 'title': 'Add Lab'})

# ----------------------------------------------------------------------------------------

@login_required(login_url='login')
def lab_update(request, pk):
    try:
        logger.info(f"Updating lab {pk} - User: {request.user.username}")
        lab = get_object_or_404(Lab, pk=pk)

        if request.method == 'POST':
            form = LabForm(request.POST, instance=lab)
            lab_name = request.POST.get("lab_name", "").strip()
            address = request.POST.get("address", "").strip()
            email = request.POST.get("email", "").strip()
            contact_no = request.POST.get("contact_no", "").strip()

            has_error = False

            # 1️⃣ Required fields
            if not lab_name or not address or not email or not contact_no:
                messages.error(request, "All fields are required.")
                has_error = True

            # 2️⃣ Contact number validation
            elif not re.fullmatch(r"^[6-9]\d{9}$", contact_no):
                messages.error(request, "Enter a valid 10-digit contact number starting with 6–9.")
                has_error = True

            # 3️⃣ Email format
            elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                messages.error(request, "Enter a valid email address.")
                has_error = True

            # 4️⃣ Duplicate name/email check (excluding current lab)
            elif Lab.objects.filter(
                (Q(lab_name__iexact=lab_name) | Q(email__iexact=email)),
                status="Active"
            ).exclude(pk=pk).exists():
                messages.error(request, "Another lab with this name or email already exists.")
                has_error = True

            if has_error:
                logger.warning(f"Lab update validation failed for {lab_name}")
                return render(request, 'labs/lab_edit.html', {'form': form, 'lab': lab})

            # ✅ If valid, save
            if form.is_valid():
                form.save()
                logger.info(f"Lab {pk} updated successfully")
                messages.success(request, f"Lab '{lab.lab_name}' updated successfully!")
                return redirect('lab_list')
            else:
                messages.error(request, "Form contains invalid data.")
        else:
            form = LabForm(instance=lab)

    except Exception as e:
        logger.error(f"Error updating lab {pk}: {str(e)}", exc_info=True)
        messages.error(request, "An unexpected error occurred while updating the lab.")
        return redirect('lab_list')

    return render(request, 'labs/lab_edit.html', {'form': form, 'lab': lab})
# ----------------------------------------------------------------------------------------

@login_required(login_url='login')
def lab_delete(request, pk):
    try:
        logger.info(f"Deleting lab {pk} - User: {request.user.username}")
        lab = get_object_or_404(Lab, pk=pk)

        if request.method == 'POST':
            lab_name = lab.lab_name
            lab.status = 'Inactive'
            lab.save()
            messages.success(request, f"Lab '{lab_name}' deleted successfully.")
            logger.info(f"Lab {pk} ({lab_name}) marked as inactive")
            return redirect('lab_list')

    except Exception as e:
        logger.error(f"Error deleting lab {pk}: {str(e)}", exc_info=True)
        messages.error(request, "Error deleting lab. Please try again.")
        return redirect('lab_list')

    return render(request, 'labs/lab_confirm_delete.html', {'lab': lab})

import logging
logger = logging.getLogger('pathosoft')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Doctor , Lab
from .forms import DoctorForm, DoctorTransactionForm
from patient.models import PatientMaster
from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import CustomUser
from .models import Doctor, DoctorLedger, DoctorTransaction
from django.contrib import messages

    

@login_required
def add_doctor(request):
    try:
        logger.info(f"Adding new doctor - User: {request.user.username}")
        lab = request.user.lab  
        
        if request.method == 'POST':
            form = DoctorForm(request.POST)
            if form.is_valid():
                doctor = form.save(commit=False)
                doctor.lab = lab  # Automatically assign current user's lab
                doctor.save()
                logger.info(f"Doctor created successfully - ID: {doctor.id}, Name: {doctor.doctor_name}")
                messages.success(request, "Doctor added successfully!")
                return redirect('view_doctors')
            
            else:
                logger.warning(f"Doctor creation failed - Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")

    except Exception as e:
        logger.error(f"Error creating doctor: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while adding doctor.")
        return redirect('view_doctors')

    else:
        form = DoctorForm()

    return render(request, 'doctor/add_doctor.html', {'form': form})

@login_required(login_url='login')
def view_doctors(request):
    lab = request.user.lab
    query = request.GET.get('q', '').strip()  # same as staff search
    doctors = Doctor.objects.filter(lab=lab,status=True).order_by('-id')

    if query:
        doctors = doctors.filter(
            Q(doctor_name__icontains=query) |
            Q(hospital_name__icontains=query) |
            Q(email__icontains=query) |
            Q(mobile_number__icontains=query) |
            Q(address__icontains=query)
        )

    paginator = Paginator(doctors, 10)  # your pagination stays
    page_number = request.GET.get('page')
    doctors_page = paginator.get_page(page_number)

    return render(request, 'doctor/view_doctors.html', {
        'doctors': doctors_page,
        'query': query,
    })

@login_required(login_url='login')
def update_doctor(request, pk):
    try:
        logger.info(f"Updating doctor {pk} - User: {request.user.username}")
        doctor = get_object_or_404(Doctor, pk=pk, lab=request.user.lab)
        
        if request.method == 'POST':
            form = DoctorForm(request.POST, instance=doctor)
            if form.is_valid():
                updated_doctor = form.save()
                logger.info(f"Doctor {pk} updated successfully")
                messages.success(request, "Doctor updated successfully!")
                return redirect('view_doctors')
            else:
                logger.warning(f"Doctor update failed - Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")
        else:
            form = DoctorForm(instance=doctor)
    except Exception as e:
        logger.error(f"Error updating doctor {pk}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while updating doctor.")
        return redirect('view_doctors')

    return render(request, 'doctor/update_doctor.html', {'form': form, 'doctor': doctor})



@login_required
def delete_doctor(request, pk):
    try:
        logger.info(f"Deleting doctor {pk} - User: {request.user.username}")
        doctor = get_object_or_404(Doctor, pk=pk, lab=request.user.lab)
        doctor_name = doctor.doctor_name
        doctor.status = False
        doctor.save()
        logger.info(f"Doctor {pk} ({doctor_name}) marked as deleted")
        messages.success(request, "Doctor deleted successfully!")
    except Exception as e:
        logger.error(f"Error deleting doctor {pk}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while deleting doctor.")
    
    return redirect('view_doctors')

@login_required
def doctor_commission(request):
    lab = request.user.lab
    doctors = Doctor.objects.filter(lab=lab)
    selected_doctor_id = request.GET.get('doctor')
    commission_percent = request.GET.get('percent', 0)

    patients = []
    total_cost = 0
    total_share = 0

    if selected_doctor_id:
        patients = PatientMaster.objects.filter(doctor_id=selected_doctor_id, lab=lab)
        commission_percent = Decimal(commission_percent) if commission_percent else Decimal('0')
        total_cost = Decimal('0')
        total_share = Decimal('0')

        for p in patients:
            total_amount = p.total_amount or Decimal('0')
            p.share = (total_amount * commission_percent / Decimal('100')) if total_amount else Decimal('0')
            total_cost += total_amount
            total_share += p.share


    return render(request, 'doctor/doctor_commission.html', {
        'doctors': doctors,
        'patients': patients,
        'selected_doctor': int(selected_doctor_id) if selected_doctor_id else '',
        'commission_percent': commission_percent,
        'total_cost': total_cost,
        'total_share': total_share,
    })

def doctor_ledger_list(request):
    ledgers = DoctorLedger.objects.select_related("doctor").all()
    return render(request, "doctor_ledger/list.html", {"ledgers": ledgers})


def doctor_ledger_detail(request, doctor_id):

    doctor = get_object_or_404(Doctor, id=doctor_id)
    ledger, _ = DoctorLedger.objects.get_or_create(doctor=doctor)
    transactions = DoctorTransaction.objects.filter(doctor=doctor).order_by('-payment_date')
    payment_date = request.GET.get('payment_date')
    transactions = transactions.filter(payment_date=payment_date) if payment_date else transactions
    print("Filtered Transactions:", transactions)
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    transactions_page = paginator.get_page(page_number)

    # ✅ Render page
    return render(
        request,
        "doctor_ledger/detail.html",
        {
            "doctor": doctor,
            "ledger": ledger,
            "transactions": transactions_page,
            "payment_date": payment_date,
        }
    )

def add_transaction(request, doctor_id):
    try:
        logger.info(f"Adding transaction for doctor {doctor_id} - User: {request.user.username}")
        doctor = get_object_or_404(Doctor, id=doctor_id)
        # Ensure `form` is always defined so GET requests don't crash
        form = DoctorTransactionForm()

        if request.method == "POST":
            form = DoctorTransactionForm(request.POST)
            amount_paid = request.POST.get("amount_paid")
            logger.debug(f"Processing transaction - Amount: {amount_paid}")

            # --- Validation Flags ---
            has_error = False

            # ✅ Validate mobile number (10 digits, starts with 6–9)
            # if not re.fullmatch(r"^[6-9]\d{9}$", str(mobile_no)):
            #     messages.error(request, "Enter a valid 10-digit mobile number starting with 6–9.")
            #     has_error = True

            # ✅ Validate amount paid
            try:
                amount = float(amount_paid)
                if amount <= 0:
                    messages.error(request, "Amount paid must be greater than 0.")
                    has_error = True
                else:
                    ledger = getattr(doctor, "doctorledger", None)
                    if ledger and amount > ledger.balance_amount:
                        messages.error(
                            request,
                            f"Amount cannot exceed current balance (₹{ledger.balance_amount})."
                        )
                        has_error = True
            except (TypeError, ValueError):
                messages.error(request, "Please enter a valid numeric amount.")
                has_error = True

            # ✅ If any validation fails, return form with errors
            if has_error:
                return render(request, "doctor_ledger/add_transaction.html", {
                    "form": form,
                    "doctor": doctor,
                })

            # ✅ If all good, save transaction
            if form.is_valid():
                transaction = form.save(commit=False)
                transaction.doctor = doctor
                transaction.save()
                logger.info(f"Transaction added successfully for doctor {doctor_id} - Amount: {amount_paid}")
                messages.success(request, "Payment added successfully!")
                return redirect("doctor_ledger_detail", doctor_id=doctor.id)
            else:
                logger.warning(f"Transaction failed - Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.title()}: {error}")
    except Exception as e:
        logger.error(f"Error adding transaction for doctor {doctor_id}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while processing the transaction.")
        return redirect("doctor_ledger_detail", doctor_id=doctor_id)

    return render(request, "doctor_ledger/add_transaction.html", {
        "form": form,
        "doctor": doctor,
    })

# def add_transaction(request, doctor_id):
#     doctor = get_object_or_404(Doctor, id=doctor_id)
#     if request.method == "POST":
#         form = DoctorTransactionForm(request.POST)
#         if form.is_valid():
#             transaction = form.save(commit=False)
#             transaction.doctor = doctor
#             transaction.save()
#             messages.success(request, "Payment added successfully!")
#             return redirect("doctor_ledger_detail", doctor_id=doctor.id)
#         else:
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"{field.title()}: {error}")
#     else:
#         form = DoctorTransactionForm()
#     return render(request, "doctor_ledger/add_transaction.html", {"form": form, "doctor": doctor})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Doctor , Lab
from .forms import DoctorForm
from patient.models import PatientMaster
from django.db.models import Sum
from decimal import Decimal
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import CustomUser

    

@login_required
def add_doctor(request):
    lab = request.user.lab  
    print("Logged-in user's lab:", lab)
    
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        print(form.data)
        print(form.errors)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.lab = lab  # Automatically assign current user's lab
            doctor.save()
            return redirect('view_doctors')

    else:
        form = DoctorForm()

    return render(request, 'doctor/add_doctor.html', {'form': form})



# ------------------------------------------------------------------------------------------------------------

# @login_required(login_url='login')
# def search_Doctors(request):
#     query = request.GET.get('docsearch', '').strip()
#     doctors = Doctor.objects.all()

#     if query:
#         doctors = doctors.filter(doctor_name__icontains=query)

#     data = []
#     for doctor in doctors:
#         data.append({
#             'id': doctor.id,
#             'doctor_id': doctor.doctor_id,
#             'doctor_name': doctor.doctor_name,
#             'email': doctor.email,
#             'mobile_number': doctor.mobile_number,
#             'hospital_name': doctor.hospital_name,
#             'address': doctor.address,
#             'lab': doctor.lab.lab_name,
#         })

#     return JsonResponse({'doctors': data})

# ------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def view_doctors(request):
    lab = request.user.lab
    query = request.GET.get('q', '').strip()  # same as staff search
    doctors = Doctor.objects.filter(lab=lab).order_by('-id')

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



# @login_required
# def view_doctors(request):
#     doctors = Doctor.objects.all().order_by('-id')     
#     paginator = Paginator(doctors, 1)
#     page_number = request.GET.get('page')
#     doctors = paginator.get_page(page_number)
#     return render(request, 'doctor/view_doctors.html', {'doctors': doctors})




@login_required(login_url='login')
def update_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk, lab=request.user.lab)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('view_doctors')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'doctor/update_doctor.html', {'form': form, 'doctor': doctor})



@login_required
def delete_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk, lab=request.user.lab)
    
    doctor.delete()
    return redirect('view_doctors')


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
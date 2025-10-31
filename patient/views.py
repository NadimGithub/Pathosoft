from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from doctor.models import Doctor
from .models import PatientMaster, PatientTest
from .forms import PatientForm, PatientTestForm
from tests.models import TestGroupMaster, TestMaster
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Prefetch

# def add_patient(request):
#     groups = TestGroupMaster.objects.filter(status=True)
#     doctors = Doctor.objects.all()
    
#     if request.method == "POST":
#         # Collect patient form data
#         patient_name = request.POST.get('patient_name')
#         title = request.POST.get('title')
#         gender = request.POST.get('gender')
#         age = request.POST.get('age')
#         mobile_number = request.POST.get('mobile_number')
#         doctor_id = request.POST.get('doctor')
#         sample_date = request.POST.get('sample_date')
#         reporting_date = request.POST.get('reporting_date')
#         weight = request.POST.get('weight')

#         # Save patient
#         doctor = Doctor.objects.get(id=doctor_id)
#         patient = PatientMaster.objects.create(
#         title=title,
#         patient_name=patient_name,
#         gender=gender,
#         age=age,
#         mobile_number=mobile_number,
#         doctor=doctor,
#         sample_date=sample_date,
#         reporting_date=reporting_date,
#         weight=weight,
#         basic_amount=request.POST.get('basic_amount') or 0,
#         extra_cost=request.POST.get('extra_cost') or 0,
#         discount=request.POST.get('discount') or 0,
#         total_amount=request.POST.get('total_amount') or 0,
#         paid_amount=request.POST.get('paid_amount') or 0,
#         balance_amount=request.POST.get('balance_amount') or 0
#     )
#         # patient = PatientMaster.objects.create(
#         #     title=title,
#         #     patient_name=patient_name,
#         #     gender=gender,
#         #     age=age,
#         #     mobile_number=mobile_number,
#         #     doctor=doctor,
#         #     sample_date=sample_date,
#         #     reporting_date=reporting_date,
#         #     weight=weight
#         # )

#         # Save selected tests
#         selected_tests = request.POST.getlist('tests[]')  # make sure JS sends test IDs
#         for test_id in selected_tests:
#             test_obj = TestMaster.objects.get(test_id=test_id)
#             PatientTest.objects.create(
#                 patient=patient,
#                 test=test_obj,
#                 cost=test_obj.cost
#             )

#         return redirect('view_patients')
    
#     return render(request, 'patients/add_patient.html', {'groups': groups, 'doctors': doctors})

def add_patient(request):
    lab = request.user.lab
    groups = TestGroupMaster.objects.filter(status=True, lab=lab)
    doctors = Doctor.objects.filter(lab=lab)

    if request.method == "POST":
        patient_name = request.POST.get('patient_name')
        title = request.POST.get('title')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        mobile_number = request.POST.get('mobile_number')
        doctor_id = request.POST.get('doctor')
        sample_date = request.POST.get('sample_date')
        reporting_date = request.POST.get('reporting_date')
        weight = request.POST.get('weight')

        # Billing fields
        basic_amount = request.POST.get('basic_amount') or 0
        extra_cost = request.POST.get('extra_cost') or 0
        discount = request.POST.get('discount') or 0
        total_amount = request.POST.get('total_amount') or 0
        paid_amount = request.POST.get('paid_amount') or 0
        balance_amount = request.POST.get('balance_amount') or 0

        doctor = Doctor.objects.get(id=doctor_id)
        patient = PatientMaster.objects.create(
            title=title,
            patient_name=patient_name,
            gender=gender,
            age=age,
            mobile_number=mobile_number,
            doctor=doctor,
            sample_date=sample_date,
            reporting_date=reporting_date,
            weight=weight,
            basic_amount=basic_amount,
            extra_cost=extra_cost,
            discount=discount,
            total_amount=total_amount,
            paid_amount=paid_amount,
            balance_amount=balance_amount,
            lab=request.user.lab
        )

        # Selected tests — split comma-separated string
        selected_tests = request.POST.get('tests', '')
        if selected_tests:
            selected_tests = selected_tests.split(',')
            for test_id in selected_tests:
                test_obj = TestMaster.objects.get(test_id=int(test_id))
                PatientTest.objects.create(
                    patient=patient,
                    test=test_obj,
                    cost=test_obj.cost
                )

         # Stay on same page but enable Print button
        return render(request, 'patients/add_patient.html', {
            'groups': groups,
            'doctors': doctors,
            'patient': patient,
            'message': 'Patient saved successfully! You can now print receipt.'
        })
        # return redirect('view_patients')

    return render(request, 'patients/add_patient.html', {'groups': groups, 'doctors': doctors})


# ----------------- EDIT PATIENT -----------------
# from django.shortcuts import render, get_object_or_404
# from .models import PatientMaster, TestMaster, TestGroupMaster, PatientTest, Doctor
def edit_patient(request, pk):
    lab = request.user.lab
    patient = get_object_or_404(PatientMaster, pk=pk)
    groups = TestGroupMaster.objects.filter(status=True)
    doctors = Doctor.objects.all()
    all_tests = TestMaster.objects.filter(status=True, lab=lab)  # ✅ added this line

       # ✅ Preload selected tests for editing
    selected_patient_tests = PatientTest.objects.filter(patient=patient)
    selected_test_ids = [pt.test.test_id for pt in selected_patient_tests]
    selected_group_ids = list(
        set(pt.test.test_group_id for pt in selected_patient_tests)
    )

    if request.method == "POST":
        # Update patient fields
        patient.title = request.POST.get('title')
        patient.patient_name = request.POST.get('patient_name')
        patient.gender = request.POST.get('gender')
        patient.age = request.POST.get('age')
        patient.mobile_number = request.POST.get('mobile_number')
        doctor_id = request.POST.get('doctor')
        patient.doctor = Doctor.objects.get(id=doctor_id) if doctor_id else None
        patient.sample_date = request.POST.get('sample_date')
        patient.reporting_date = request.POST.get('reporting_date')
        patient.weight = request.POST.get('weight')

        # Billing info
        patient.basic_amount = request.POST.get('basic_amount') or 0
        patient.extra_cost = request.POST.get('extra_cost') or 0
        patient.discount = request.POST.get('discount') or 0
        patient.total_amount = request.POST.get('total_amount') or 0
        patient.paid_amount = request.POST.get('paid_amount') or 0
        patient.balance_amount = request.POST.get('balance_amount') or 0
        patient.save()

        # Update selected tests
        PatientTest.objects.filter(patient=patient).delete()
        selected_tests = request.POST.get('tests', '')
        print("Selected Tests String:", selected_tests)  # Debugging line
        if selected_tests:
            for test_id in selected_tests.split(','):
                test_obj = TestMaster.objects.get(test_id=int(test_id))
                PatientTest.objects.create(
                    patient=patient,
                    test=test_obj,
                    cost=test_obj.cost
                )

        return render(request, 'patients/edit_patient.html', {
            'patient': patient,
            'groups': groups,
            'tests': all_tests,
            'doctors': doctors,
            'selected_tests': selected_patient_tests,   # ✅ ADD THIS LINE
            'selected_test_ids': selected_test_ids,
            'selected_group_ids': selected_group_ids,
            'is_edit': True,
            'message': 'Patient updated successfully!'
        })

   # ✅ Preload selected tests for editing
    # selected_patient_tests = PatientTest.objects.filter(patient=patient)
    # selected_test_ids = [pt.test.test_id for pt in selected_patient_tests]
    # selected_group_ids = list(
    #     set(pt.test.test_group_id for pt in selected_patient_tests)
    # )

    return render(request, 'patients/edit_patient.html', {
        'patient': patient,
        'groups': groups,
        'tests': all_tests,
        'doctors': doctors,
        'selected_tests': selected_patient_tests,   # ✅ ADD THIS LINE
        'selected_test_ids': selected_test_ids,
        'selected_group_ids': selected_group_ids,
        'is_edit': True
    })
# def edit_patient(request, pk):
#     patient = get_object_or_404(PatientMaster, pk=pk)
#     groups = TestGroupMaster.objects.filter(status=True)
#     doctors = Doctor.objects.all()
#     all_tests = TestMaster.objects.filter(status=True)

#     if request.method == "POST":
#         # --- Update Patient Info ---
#         patient.title = request.POST.get('title')
#         patient.patient_name = request.POST.get('patient_name')
#         patient.gender = request.POST.get('gender')
#         patient.age = request.POST.get('age')
#         patient.mobile_number = request.POST.get('mobile_number')
#         doctor_id = request.POST.get('doctor')
#         patient.doctor = Doctor.objects.get(id=doctor_id) if doctor_id else None
#         patient.sample_date = request.POST.get('sample_date')
#         patient.reporting_date = request.POST.get('reporting_date')
#         patient.weight = request.POST.get('weight')

#         # --- Billing ---
#         patient.basic_amount = request.POST.get('basic_amount') or 0
#         patient.extra_cost = request.POST.get('extra_cost') or 0
#         patient.discount = request.POST.get('discount') or 0
#         patient.total_amount = request.POST.get('total_amount') or 0
#         patient.paid_amount = request.POST.get('paid_amount') or 0
#         patient.balance_amount = request.POST.get('balance_amount') or 0
#         patient.save()

#         # --- Update Selected Tests ---
#         selected_tests_str = request.POST.get('tests', '')
#         selected_test_ids = [int(tid) for tid in selected_tests_str.split(',') if tid.strip().isdigit()]

#         # Delete old tests, then reinsert the selected ones
#         PatientTest.objects.filter(patient=patient).delete()
#         for test_id in selected_test_ids:
#             test_obj = TestMaster.objects.get(test_id=test_id)
#             PatientTest.objects.create(
#                 patient=patient,
#                 test=test_obj,
#                 cost=test_obj.cost
#             )

#         # ✅ Stay on same page after update
#         return render(request, 'patients/edit_patient.html', {
#             'groups': groups,
#             'doctors': doctors,
#             'patient': patient,
#             'is_edit': True,
#             'tests': all_tests,
#             'message': '✅ Patient updated successfully!',
#         })

#     # --- For GET request ---
#     selected_patient_tests = PatientTest.objects.filter(patient=patient)
#     selected_test_ids = [pt.test.test_id for pt in selected_patient_tests]
#     selected_group_ids = list(set(pt.test.test_group_id for pt in selected_patient_tests))

#     return render(request, 'patients/edit_patient.html', {
#         'patient': patient,
#         'groups': groups,
#         'tests': all_tests,
#         'doctors': doctors,
#         'selected_tests': selected_patient_tests,
#         'selected_test_ids': selected_test_ids,
#         'selected_group_ids': selected_group_ids,
#         'is_edit': True
#     })

def get_tests_by_group(request, group_id):
    lab = request.user.lab
    tests = TestMaster.objects.filter(test_group_id=group_id, status=True, lab=lab)
    data = []
    for t in tests:
        normal_range = f"{t.lower_range} - {t.upper_range}" if t.lower_range and t.upper_range else "-"
        data.append({
            "test_id": t.test_id,
            "test_name": t.test_name,
            "normal_range": normal_range,
            "units": t.units,
            "cost": t.cost,
        })
    return JsonResponse(list(data), safe=False)

# def get_tests_by_group(request, group_id):
#     tests = TestMaster.objects.filter(test_group_id=group_id, status=True).values(
#         'test_id', 'test_name', 'normal_range', 'units', 'cost'
#     )
#     return JsonResponse(list(tests), safe=False)




def print_receipt(request, patient_id):
    patient = get_object_or_404(PatientMaster, pk=patient_id)
    tests = PatientTest.objects.filter(patient=patient)
    total_cost = sum(test.cost for test in tests)
    date = timezone.now().strftime("%d-%m-%Y")

    html_content = render_to_string('patients/receipt.html', {
        'patient': patient,
        'tests': tests,
        'date': date,
        'total_cost': total_cost,
    })
    return HttpResponse(html_content)


def view_patients(request): 
    lab = request.user.lab
    query = request.GET.get('q', '').strip()
    patients = PatientMaster.objects.filter(lab=lab).order_by('patient_id')

    if query:
        patients = patients.filter(
             Q(patient_id__icontains=query) |
            Q(patient_name__icontains=query) |
            Q(mobile_number__icontains=query) 
            
        )

    paginator = Paginator(patients, 10)  # Adjust per-page count as needed
    page_number = request.GET.get('page')
    patients_page = paginator.get_page(page_number)

    return render(request, 'patients/view_patients.html', {
        'patients': patients_page,
        'query': query,
    })

# def update_patient(request, pk):
#     patient = get_object_or_404(PatientMaster, pk=pk)
#     tests = TestMaster.objects.all()
#     if request.method == 'POST':
#         form = PatientForm(request.POST, instance=patient)
#         if form.is_valid():
#             form.save()
#             PatientTest.objects.filter(patient=patient).delete()
#             selected_tests = request.POST.getlist('tests')
#             for test_id in selected_tests:
#                 test_obj = TestMaster.objects.get(id=test_id)
#                 PatientTest.objects.create(
#                     patient=patient,
#                     test=test_obj,
#                     cost=test_obj.cost
#                 )
#             return redirect('view_patients')
#     else:
#         form = PatientForm(instance=patient)
#         selected_tests = patient.tests.values_list('test_id', flat=True)
#     return render(request, 'patients/update_patient.html', {'form': form, 'tests': tests, 'selected_tests': selected_tests})


def delete_patient(request, pk):
    patient = get_object_or_404(PatientMaster, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('view_patients')
    return render(request, 'patients/delete_confirm.html', {'patient': patient})




def generate_report(request, patient_id):
    patient = get_object_or_404(PatientMaster, pk=patient_id)
    patient_tests = PatientTest.objects.filter(patient=patient).select_related('test', 'test__test_group')

    if request.method == 'POST':
        for test in patient_tests:
            result = request.POST.get(f'result_{test.id}')
            notes = request.POST.get(f'notes_{test.id}')
            remarks = request.POST.get(f'remarks_{test.id}')
            
            test.result_value = result
            test.notes = notes
            test.remarks = remarks
            test.save()
        
        return redirect('generate_report', patient_id=patient.patient_id)

    grouped_tests = {}
    for t in patient_tests:
        group_name = t.test.test_group.group_name
        if group_name not in grouped_tests:
            grouped_tests[group_name] = []
        grouped_tests[group_name].append(t)

    return render(request, 'patients/generate_report.html', {
        'patient': patient,
        'grouped_tests': grouped_tests
    })

from decimal import Decimal, InvalidOperation

def print_test_report(request, patient_id):
    user = request.user
    patient = get_object_or_404(PatientMaster, pk=patient_id)
    patient_tests = PatientTest.objects.select_related('test__test_group').filter(patient=patient)

    grouped_tests = {}
    for pt in patient_tests:
        result_val = None
        if pt.result_value is not None:
            try:
                # Convert result_value to Decimal if possible
                result_val = Decimal(str(pt.result_value))
            except (InvalidOperation, TypeError, ValueError):
                result_val = None

        # Default styles
        pt.bg_color = ''
        pt.status_label = ''

        # Only compare if we successfully converted to Decimal
        if result_val is not None:
            lower = pt.test.lower_range
            upper = pt.test.upper_range

            if lower is not None and result_val < lower:
                pt.bg_color = "#e6f331"   # yellow = low
                pt.status_label = 'Low'
            elif upper is not None and result_val > upper:
                pt.bg_color = "#ff6060"   # light yellow = high
                pt.status_label = 'High'

        # Group tests by their group name
        group_name = pt.test.test_group.group_name if pt.test.test_group else "Other"
        grouped_tests.setdefault(group_name, []).append(pt)

    context = {
        'patient': patient,
        'grouped_tests': grouped_tests,
        'user': user,
    }
    return render(request, 'patients/print_test_report.html', context)

# def print_test_report(request, patient_id):
#     patient = get_object_or_404(PatientMaster, pk=patient_id)
#     patient_tests = PatientTest.objects.select_related('test__test_group').filter(patient=patient)

#     grouped_tests = {}
#     for pt in patient_tests:
#         group_name = pt.test.test_group.group_name if pt.test.test_group else "Other"
#         grouped_tests.setdefault(group_name, []).append(pt)

#     context = {
#         'patient': patient,
#         'grouped_tests': grouped_tests,
#     }
#     return render(request, 'patients/print_test_report.html', context)
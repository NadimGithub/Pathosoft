import logging
logger = logging.getLogger('pathosoft')

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from doctor.models import Doctor
from .models import PatientMaster, PatientTest, DoctorCommission
from .forms import PatientForm, PatientTestForm
from tests.models import Methods, TestGroupMaster, TestMaster
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Prefetch
from doctor.models import DoctorLedger
from decimal import Decimal
from django.db.models import Sum
from django.contrib import messages
from decimal import Decimal, InvalidOperation


def add_patient(request):
    try:
        logger.info(f"Adding new patient - User: {request.user.username}")
        lab = request.user.lab
        groups = TestGroupMaster.objects.filter(status=True, lab=lab)
        doctors = Doctor.objects.filter(lab=lab,status=True)
        methods = Methods.objects.filter(lab=lab, status=True)
   
        if request.method == "POST":
            patient_name = request.POST.get('patient_name')
            logger.debug(f"Processing new patient data: {patient_name}")
            title = request.POST.get('title')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            mobile_number = request.POST.get('mobile_number')
            doctor_id = request.POST.get('doctor')
            sample_date = request.POST.get('sample_date')
            reporting_date = request.POST.get('reporting_date')
            weight = request.POST.get('weight')
            blood_group = request.POST.get('blood_group')
            address = request.POST.get('address')

            # Billing fields
            basic_amount = request.POST.get('basic_amount') or 0
            extra_cost = request.POST.get('extra_cost') or 0
            discount = request.POST.get('discount') or 0
            total_amount = request.POST.get('total_amount') or 0
            paid_amount = request.POST.get('paid_amount') or 0
            balance_amount = request.POST.get('balance_amount') or 0

             # 🛑 Basic validation
            if not patient_name:
                logger.warning("Patient creation failed: Missing name")
                messages.error(request, "Patient name is required.")
                return redirect('add_patient')
            if not gender:
                messages.error(request, "Please select gender.")
                return redirect('add_patient')
            if not age or not age.isdigit() or int(age) <= 0:
                messages.error(request, "Enter a valid age.")
                return redirect('add_patient')
            if mobile_number and len(mobile_number) != 10:
                messages.error(request, "Enter a valid mobile number.")
                return redirect('add_patient')
            if not sample_date or not reporting_date:
                messages.error(request, "Please provide sample and reporting dates.")
                return redirect('add_patient')

            # 🧮 Logical validation
            if Decimal(paid_amount) > Decimal(total_amount):
                messages.error(request, "Paid amount cannot exceed total amount.")
                return redirect('add_patient')

            if doctor_id == '0':
                doctor = None
            else:
                doctor = get_object_or_404(Doctor, id=doctor_id)

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
                blood_group=blood_group,
                address=address,
                basic_amount=basic_amount,
                extra_cost=extra_cost,
                discount=discount,
                total_amount=total_amount,
                paid_amount=paid_amount,
                balance_amount=balance_amount,
                lab=request.user.lab
            )
            logger.info(f"Patient created successfully - ID: {patient.patient_id}, Name: {patient_name}")

            # Selected tests — split comma-separated string
            selected_tests = request.POST.get('tests', '')
            if selected_tests:
                logger.debug(f"Adding tests for patient {patient.patient_id}: {selected_tests}")
                selected_tests = selected_tests.split(',')
                for test_id in selected_tests:
                    test_obj = TestMaster.objects.get(test_id=int(test_id))
                    PatientTest.objects.create(
                        patient=patient,
                        test=test_obj,
                        cost=test_obj.cost
                    )

            # Commission handling
            if patient.doctor:
                logger.debug(f"Processing commission for doctor {patient.doctor.doctor_name}")
                try:
                    total_amount = Decimal(str(patient.total_amount))  # ✅ Convert to Decimal safely
                except (InvalidOperation, TypeError, ValueError):
                    total_amount = Decimal("0.00")

                if total_amount > 0:
                    doctor = patient.doctor
                    commission_percent = doctor.commission_percent or Decimal("0.00")
                    commission_amount = (total_amount * commission_percent) / 100

                    DoctorCommission.objects.create(
                        doctor=doctor,
                        patient=patient,
                        commission_percent=commission_percent,
                        commission_amount=commission_amount,
                    )

                    # ✅ Update Doctor Ledger
                    ledger, _ = DoctorLedger.objects.get_or_create(doctor=doctor)
                    ledger.total_commission += commission_amount
                    ledger.update_balance()

            logger.info(f"Patient creation completed - ID: {patient.patient_id}")
            messages.success(request, f"Patient '{patient.patient_name}' created successfully!")
            return redirect('view_patients')

    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while creating patient.")
        return redirect('add_patient')

    return render(request, 'patients/add_patient.html', {'groups': groups, 'doctors': doctors, 'methods': methods })

def edit_patient(request, pk):
    try:
        logger.info(f"Editing patient {pk} - User: {request.user.username}")
        lab = request.user.lab
        patient = get_object_or_404(PatientMaster, pk=pk)
        methods = Methods.objects.filter(lab=lab, status=True)
        groups = TestGroupMaster.objects.filter(status=True)
        doctors = Doctor.objects.filter(lab=lab)
        all_tests = TestMaster.objects.filter(status=True, lab=lab)  # ✅ added this line

           # ✅ Preload selected tests for editing
        selected_patient_tests = PatientTest.objects.filter(patient=patient)
        selected_test_ids = [pt.test.test_id for pt in selected_patient_tests]
        selected_group_ids = list(
            set(pt.test.test_group_id for pt in selected_patient_tests)
        )

        if request.method == "POST":
            logger.debug(f"Processing edit for patient {pk}")
            # Update patient fields
            patient.title = request.POST.get('title')
            patient.patient_name = request.POST.get('patient_name')
            patient.gender = request.POST.get('gender')
            patient.age = request.POST.get('age')
            patient.mobile_number = request.POST.get('mobile_number')

            if not patient.patient_name:
                messages.error(request, "Patient name cannot be empty.")
                return redirect('edit_patient', pk=pk)
            if patient.mobile_number and len(patient.mobile_number) != 10:
                messages.error(request, "Invalid mobile number.")
                return redirect('edit_patient', pk=pk)
            if not patient.age or not patient.age.isdigit():
                messages.error(request, "Invalid age entered.")
                return redirect('edit_patient', pk=pk)


            doctor_id = request.POST.get('doctor')
            if doctor_id == '0':
                doctor = None
            else:
                doctor = get_object_or_404(Doctor, id=doctor_id)
            patient.doctor = doctor
            patient.sample_date = request.POST.get('sample_date')
            patient.reporting_date = request.POST.get('reporting_date')
            patient.weight = request.POST.get('weight')
            patient.blood_group = request.POST.get('blood_group')
            patient.address = request.POST.get('address')

            # Billing info
            patient.basic_amount = request.POST.get('basic_amount') or 0
            patient.extra_cost = request.POST.get('extra_cost') or 0
            patient.discount = request.POST.get('discount') or 0
            patient.total_amount = request.POST.get('total_amount') or 0
            patient.paid_amount = request.POST.get('paid_amount') or 0
            patient.balance_amount = request.POST.get('balance_amount') or 0
            patient.save()
            logger.info(f"Patient {pk} updated successfully")

            # Update selected tests
            PatientTest.objects.filter(patient=patient).delete()
            selected_tests = request.POST.get('tests', '')
            logger.debug(f"Updating tests for patient {pk}: {selected_tests}")
            if selected_tests:
                for test_id in selected_tests.split(','):
                    test_obj = TestMaster.objects.get(test_id=int(test_id))
                    PatientTest.objects.create(
                        patient=patient,
                        test=test_obj,
                        cost=test_obj.cost
                    )
            
            # ✅ Automatically create doctor commission entry
            if patient.doctor:
                try:
                    total_amount = Decimal(str(patient.total_amount))
                except (InvalidOperation, TypeError, ValueError):
                    total_amount = Decimal("0.00")

                if total_amount > 0:
                    doctor = patient.doctor
                    commission_percent = doctor.commission_percent or Decimal("0.00")
                    commission_amount = (total_amount * commission_percent) / 100

                    # ✅ Check if commission already exists
                    existing_commission = DoctorCommission.objects.filter(
                        doctor=doctor,
                        patient=patient
                    ).first()

                    if existing_commission:
                        # Update existing commission instead of creating new one
                        difference = commission_amount - existing_commission.commission_amount
                        existing_commission.commission_percent = commission_percent
                        existing_commission.commission_amount = commission_amount
                        existing_commission.save()

                        # Update ledger only by difference
                        ledger, _ = DoctorLedger.objects.get_or_create(doctor=doctor)
                        ledger.total_commission += difference
                        ledger.update_balance()

                    else:
                        # Create new commission only if not exists
                        DoctorCommission.objects.create(
                            doctor=doctor,
                            patient=patient,
                            commission_percent=commission_percent,
                            commission_amount=commission_amount,
                        )

                        ledger, _ = DoctorLedger.objects.get_or_create(doctor=doctor)
                        ledger.total_commission += commission_amount
                        ledger.update_balance()
       
            messages.success(request, f"Patient '{patient.patient_name}' updated successfully!")
            return redirect('view_patients')

    except Exception as e:
        logger.error(f"Error editing patient {pk}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while updating patient.")
        return redirect('edit_patient', pk=pk)

    return render(request, 'patients/edit_patient.html', {
        'patient': patient,
        'groups': groups,
        'tests': all_tests,
        'doctors': doctors,
        'methods': methods,
        'selected_tests': selected_patient_tests,   # ✅ ADD THIS LINE
        'selected_test_ids': selected_test_ids,
        'selected_group_ids': selected_group_ids,
        'is_edit': True
    })

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
            "compulsory": t.compulsory,
        })
    return JsonResponse(list(data), safe=False)

def print_receipt(request, patient_id):
    patient = get_object_or_404(PatientMaster, pk=patient_id)
    tests = PatientTest.objects.filter(patient=patient,status=True)

    # ✅ Group by test group
    grouped_tests = (
        tests.values('test__test_group__group_name')  # adjust field name as per your model
        .annotate(total_cost=Sum('cost'))
        .order_by('test__test_group__group_name')
    )

    date = timezone.now().strftime("%d-%m-%Y")

    html_content = render_to_string('patients/receipt.html', {
        'patient': patient,
        'grouped_tests': grouped_tests,
        'date': date,
    })

    return HttpResponse(html_content)

def view_patients(request): 
    lab = request.user.lab
    query = request.GET.get('q', '').strip()
    patients = PatientMaster.objects.filter(lab=lab,status=True).order_by('-patient_id')

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

def delete_patient(request, pk):
    try:
        patient = get_object_or_404(PatientMaster, pk=pk)
        logger.info(f"Deleting patient {pk} - User: {request.user.username}")
        
        if request.method == 'POST':
            patient_name = patient.patient_name
            patient.status = False
            patient.save()
            logger.info(f"Patient {pk} ({patient_name}) marked as deleted")
            messages.success(request, f"Patient '{patient.patient_name}' deleted successfully!")
            return redirect('view_patients')
    except Exception as e:
        logger.error(f"Error deleting patient {pk}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while deleting patient.")
        return redirect('view_patients')

    return render(request, 'patients/delete_confirm.html', {'patient': patient})

def generate_report(request, patient_id):
    try:
        logger.info(f"Generating report for patient {patient_id}")
        patient = get_object_or_404(PatientMaster, pk=patient_id)
        patient_tests = PatientTest.objects.filter(patient=patient).select_related('test', 'test__test_group')

        if request.method == 'POST':
            logger.debug(f"Processing test results for patient {patient_id}")
            all_filled = True
            for test in patient_tests:
                result = request.POST.get(f'result_{test.id}')
                notes = request.POST.get(f'notes_{test.id}')
                remarks = request.POST.get(f'remarks_{test.id}')
                
                test.result_value = result
                test.notes = notes
                test.remarks = remarks
                test.save()

                if not result:
                    all_filled = False
            
            patient.report_status = "Completed" if all_filled else "Pending"
            patient.save()
            messages.success(request, f"Report Results for '{patient.patient_name}' updated successfully!")
            logger.info(f"Report status updated to {patient.report_status} for patient {patient_id}")
            
    except Exception as e:
        logger.error(f"Error generating report for patient {patient_id}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while generating the report.")
        return redirect('view_patients')

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



def print_test_report(request, patient_id):
    user = request.user
    patient = get_object_or_404(PatientMaster, pk=patient_id)
    patient_tests = PatientTest.objects.select_related(
        'test__test_group__department'
    ).filter(patient=patient)

    grouped_departments = {}

    for pt in patient_tests:
        raw_value = str(pt.result_value).strip() if pt.result_value else None
        pt.bg_color = ''
        pt.text_color = '#000000'
        pt.text_decoration = 'none'
        pt.font_weight = 'normal'
        pt.status_label = ''

        result_val = None
        is_numeric = False

        # ✅ Try numeric conversion
        if raw_value is not None:
            try:
                result_val = Decimal(raw_value)
                is_numeric = True
            except (InvalidOperation, TypeError, ValueError):
                is_numeric = False

        # ✅ Logic for numeric tests
        # ✅ Logic for numeric tests
            if is_numeric:
                lower = pt.test.lower_range
                upper = pt.test.upper_range

                try:
                    lower = Decimal(str(lower)) if lower is not None else None
                except (InvalidOperation, TypeError, ValueError):
                    lower = None

                try:
                    upper = Decimal(str(upper)) if upper is not None else None
                except (InvalidOperation, TypeError, ValueError):
                    upper = None

                if lower is not None and result_val < lower:
                    pt.text_decoration = "underline"
                    pt.font_weight = "bold"
                    pt.status_label = 'Low'
                    pt.bg_color = "rgba(144, 238, 144, 0.4)"  # ✅ light green shadow effect
                elif upper is not None and result_val > upper:
                    pt.text_decoration = "underline"
                    pt.font_weight = "bold"
                    pt.status_label = 'High'
                    pt.bg_color = "rgba(144, 238, 144, 0.4)"  # ✅ light green shadow effect
                else:
                    pt.font_weight = "bold"
                    pt.status_label = 'Normal'


        # ✅ Logic for text-based results
            elif raw_value:
                val = raw_value.strip().lower()
                if val in ['-', 'negative', '(-)']:
                    pt.text_decoration = "none"
                    pt.font_weight = "bold"
                    pt.status_label = 'Normal'
                elif val in ['+', 'positive', '(+)']:
                   
                    pt.font_weight = "bold"
                    pt.status_label = 'High'
                    pt.bg_color = "rgba(144, 238, 144, 0.4)"  # ✅ light green shadow effect
                    
                else:
                    pt.font_weight = "bold"
                    pt.status_label = raw_value


        # ✅ Group by department and test group
        dept_name = pt.test.test_group.department.department_name if pt.test.test_group and pt.test.test_group.department else "Other Department"
        group_name = pt.test.test_group.group_name if pt.test.test_group else "Other Tests"

        grouped_departments.setdefault(dept_name, {}).setdefault(group_name, []).append(pt)

    context = {
        'patient': patient,
        'grouped_departments': grouped_departments,
        'user': user,
    }
    return render(request, 'patients/print_test_report.html', context)

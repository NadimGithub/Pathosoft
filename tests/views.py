import logging
logger = logging.getLogger('pathosoft')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Methods, TestDepartmentMaster, TestMaster, TestGroupMaster
from .forms import MethodForm, TestForm, TestGroupForm, DepartmentForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import traceback


# ---------- DEPARTMENT ----------
@login_required
def department_list(request):
    try:
        logger.info(f"User '{request.user.username}' accessed department list.")
        query = request.GET.get('q', '').strip()
        lab = request.user.lab
        departments = TestDepartmentMaster.objects.filter(lab=lab, status=True).order_by('-department_name')

        if query:
            logger.debug(f"Filtering departments with query: {query}")
            departments = departments.filter(department_name__icontains=query)

        paginator = Paginator(departments, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'tests/department_list.html', {'departments': page_obj, 'query': query})
    except Exception as e:
        logger.error(f"Error loading department list: {str(e)}", exc_info=True)
        messages.error(request, "Error loading department list.")
        return redirect('dashboard')


@login_required
def department_create(request):
    try:
        logger.info(f"User '{request.user.username}' is creating a new department.")
        lab = request.user.lab

        if request.method == "POST":
            department_name = request.POST.get('department_name', '').strip()

            if not department_name:
                messages.error(request, "Department name cannot be empty.")
                logger.warning("Department creation failed: Empty name.")
                return redirect('department_list')

            if TestDepartmentMaster.objects.filter(department_name__iexact=department_name, lab=lab, status=True).exists():
                messages.error(request, "This department already exists in your lab.")
                logger.warning(f"Duplicate department attempt: {department_name}")
                return redirect('department_list')

            department = TestDepartmentMaster.objects.create(department_name=department_name, lab=lab)
            logger.info(f"Department '{department_name}' created successfully (ID: {department.dept_id}).")
            messages.success(request, "Department added successfully!")
            return redirect('department_list')

        form = DepartmentForm()
        return render(request, 'tests/add_department.html', {'form': form, 'title': 'Add Department'})

    except Exception as e:
        logger.error(f"Error creating department: {str(e)}", exc_info=True)
        messages.error(request, "Error creating department.")
        return redirect('department_list')


@login_required
def department_update(request, dept_id):
    try:
        logger.info(f"User '{request.user.username}' is updating department ID {dept_id}.")
        lab = request.user.lab
        department = get_object_or_404(TestDepartmentMaster, pk=dept_id, lab=lab)
        if request.method == "POST":
            form = DepartmentForm(request.POST, instance=department)
            if form.is_valid():
                form.save()
                logger.info(f"Department '{department.department_name}' updated successfully.")
                messages.success(request, "Department updated successfully!")
                return redirect('department_list')
            else:
                logger.warning(f"Department update failed: {form.errors}")
        else:
            form = DepartmentForm(instance=department)
        return render(request, 'tests/edit_department.html', {'form': form, 'title': 'Edit Department'})
    except Exception as e:
        logger.error(f"Error updating department: {str(e)}", exc_info=True)
        messages.error(request, "Error updating department.")
        return redirect('department_list')

@login_required
def department_delete(request, dept_id):
    try:
        logger.info(f"User '{request.user.username}' deleting department ID {dept_id}.")
        department = get_object_or_404(TestDepartmentMaster, pk=dept_id)
        if request.method == "POST":
            department.status = False
            department.save()
            logger.info(f"Department '{department.department_name}' marked inactive.")
            messages.success(request, "Department deleted successfully!")
            return redirect('department_list')
        return render(request, 'tests/department_confirm_delete.html', {'department': department})
    except Exception as e:
        logger.error(f"Error deleting department: {str(e)}", exc_info=True)
        messages.error(request, "Error deleting department.")
        return redirect('department_list')


# ---------- TEST GROUP ----------
@login_required
def add_test_group(request):
    try:
        logger.info(f"User '{request.user.username}' is creating a new test group.")
        lab = request.user.lab
        departments = TestDepartmentMaster.objects.filter(lab=lab, status=True)

        if request.method == 'POST':
            group_name = request.POST.get('group_name', '').strip()
            department_id = request.POST.get('department')

            if not group_name or not department_id:
                messages.error(request, "All fields are required.")
                logger.warning("Test group creation failed: Missing fields.")
                return redirect('view_test_groups')

            if TestGroupMaster.objects.filter(group_name__iexact=group_name, department_id=department_id, lab=lab, status=True).exists():
                messages.error(request, "This group already exists.")
                logger.warning(f"Duplicate test group: {group_name}")
                return redirect('view_test_groups')

            department = get_object_or_404(TestDepartmentMaster, pk=department_id, lab=lab)
            TestGroupMaster.objects.create(group_name=group_name, department=department, lab=lab)
            logger.info(f"Test group '{group_name}' created successfully.")
            messages.success(request, "Test group added successfully!")
            return redirect('view_test_groups')

        form = TestGroupForm()
        return render(request, 'tests/add_test_group.html', {'form': form, 'departments': departments})
    except Exception as e:
        logger.error(f"Error adding test group: {str(e)}", exc_info=True)
        messages.error(request, "Error adding test group.")
        return redirect('view_test_groups')

@login_required
def view_test_groups(request):
    try:
        logger.info(f"User '{request.user.username}' accessed test group list.")
        lab = request.user.lab
        query = request.GET.get('q', '').strip()
        groups = TestGroupMaster.objects.filter(lab=lab, status=True).order_by('-id')

        if query:
            groups = groups.filter(group_name__icontains=query)
            logger.debug(f"Filtering test groups with query: {query}")

        paginator = Paginator(groups, 10)
        page_number = request.GET.get('page')
        groups_page = paginator.get_page(page_number)
        return render(request, 'tests/view_test_groups.html', {'groups': groups_page, 'query': query})
    except Exception as e:
        logger.error(f"Error loading test group list: {str(e)}", exc_info=True)
        messages.error(request, "Error loading test groups.")
        return redirect('dashboard')


@login_required
def update_test_group(request, pk):
    try:
        logger.info(f"User '{request.user.username}' updating test group ID {pk}.")
        lab = request.user.lab
        group = get_object_or_404(TestGroupMaster, pk=pk, lab=lab)
        departments = TestDepartmentMaster.objects.filter(lab=lab, status=True)
        if request.method == 'POST':
            form = TestGroupForm(request.POST, instance=group)
            if form.is_valid():
                form.save()
                logger.info(f"Test group '{group.group_name}' updated successfully.")
                messages.success(request, "Test group updated successfully!")
                return redirect('view_test_groups')
            else:
                logger.warning(f"Test group update failed: {form.errors}")
        else:
            form = TestGroupForm(instance=group)
        return render(request, 'tests/update_testgroup.html', {'form': form, 'departments': departments})
    except Exception as e:
        logger.error(f"Error updating test group: {str(e)}", exc_info=True)
        messages.error(request, "Error updating test group.")
        return redirect('view_test_groups')


@login_required
def delete_test_group(request, pk):
    try:
        logger.info(f"User '{request.user.username}' deleting test group ID {pk}.")
        group = get_object_or_404(TestGroupMaster, pk=pk)
        group.status = False
        group.save()
        logger.info(f"Test group '{group.group_name}' marked inactive.")
        messages.success(request, "Test group deleted successfully!")
        return redirect('view_test_groups')
    except Exception as e:
        logger.error(f"Error deleting test group: {str(e)}", exc_info=True)
        messages.error(request, "Error deleting test group.")
        return redirect('view_test_groups')


# ---------- TEST MASTER ----------
@login_required
def add_test(request):
    try:
        logger.info(f"User '{request.user.username}' adding new test.")
        lab = request.user.lab

        if request.method == 'POST':
            test_name = request.POST.get('test_name', '').strip()
            test_group_id = request.POST.get('test_group')
            methods_id = request.POST.get('methods')
            lower = request.POST.get('lower_range') or None
            upper = request.POST.get('upper_range') or None
            units = request.POST.get('units', '').strip()
            cost = request.POST.get('cost') or 0
            notes = request.POST.get('notes', '').strip()

            if not test_name or not test_group_id:
                logger.warning("Test creation failed: Missing required fields.")
                messages.error(request, "Test name and group are required.")
                return redirect('view_tests')

            if TestMaster.objects.filter(test_name__iexact=test_name, test_group_id=test_group_id, lab=lab, status=True).exists():
                logger.warning(f"Duplicate test: {test_name}")
                messages.error(request, "This test already exists.")
                return redirect('view_tests')

            test_group = get_object_or_404(TestGroupMaster, pk=test_group_id, lab=lab)
            method = Methods.objects.filter(pk=methods_id, lab=lab).first() if methods_id else None
            TestMaster.objects.create(
                test_name=test_name, test_group=test_group, methods=method,
                lower_range=lower, upper_range=upper, units=units, cost=cost,
                notes=notes, lab=lab
            )
            logger.info(f"Test '{test_name}' created successfully.")
            messages.success(request, "Test added successfully!")
            return redirect('view_tests')

        form = TestForm()
        methods = Methods.objects.filter(lab=lab, status=True)
        return render(request, 'tests/add_test.html', {'form': form, 'methods': methods})
    except Exception as e:
        logger.error(f"Error adding test: {str(e)}", exc_info=True)
        messages.error(request, "Error adding test.")
        return redirect('view_tests')

@login_required(login_url='login')
def view_tests(request):
    query = request.GET.get('q', '').strip()
    
    # Fetch tests related to logged-in user's lab
    tests = TestMaster.objects.filter(lab=request.user.lab,status=True).order_by('-test_id')

    # Optional search across multiple fields
    if query:
        tests = tests.filter(
            Q(test_name__icontains=query) |
            Q(test_group__group_name__icontains=query) |  # assuming group_name field in TestGroupMaster
            Q(units__icontains=query) |
            Q(notes__icontains=query)
        )

    # Pagination
    paginator = Paginator(tests, 10)  # 5 tests per page
    page_number = request.GET.get('page')
    tests_page = paginator.get_page(page_number)

    return render(request, 'tests/view_tests.html', {
        'tests': tests_page,
        'query': query,
    })


@login_required(login_url='login')
def update_test(request, pk):
    try:
        lab = request.user.lab
        test = get_object_or_404(TestMaster, pk=pk, lab=lab)
        methods = Methods.objects.filter(lab=lab,status=True)

        if request.method == 'POST':
            form = TestForm(request.POST, instance=test)

            if form.is_valid():
                # Extract values for validation
                test_name = request.POST.get('test_name', '').strip()
                lower = request.POST.get('lower_range', '').strip()
                upper = request.POST.get('upper_range', '').strip()
                cost = request.POST.get('cost', '').strip()
                method_id = request.POST.get('methods')

                # ✅ Validate test name
                if not test_name:
                    messages.error(request, "Test name cannot be empty.")
                    logger.warning("Validation failed: Empty test name.")
                    return redirect('view_tests')

                # ✅ Check for duplicate test (excluding self)
                if TestMaster.objects.filter(
                    test_name__iexact=test_name, 
                    lab=lab, 
                    status=True
                ).exclude(pk=pk).exists():
                    messages.error(request, "A test with this name already exists.")
                    logger.warning(f"Duplicate test name: {test_name}")
                    return redirect('view_tests')

                # ✅ Validate numeric ranges
                try:
                    if lower and upper and float(lower) >= float(upper):
                        messages.error(request, "Lower range must be less than upper range.")
                        logger.warning(f"Invalid range: lower={lower}, upper={upper}")
                        return redirect('view_tests')
                except ValueError:
                    messages.error(request, "Range values must be numeric.")
                    logger.warning("Invalid numeric input in range fields.")
                    return redirect('view_tests')

                # ✅ Validate cost
                try:
                    if cost and float(cost) < 0:
                        messages.error(request, "Cost cannot be negative.")
                        logger.warning(f"Negative cost entered: {cost}")
                        return redirect('view_tests')
                except ValueError:
                    messages.error(request, "Invalid cost value.")
                    logger.warning("Invalid cost input.")
                    return redirect('view_tests')

                # ✅ Validate method (optional but must exist)
                method = None
                if method_id:
                    try:
                        method = Methods.objects.get(pk=method_id, lab=lab)
                    except Methods.DoesNotExist:
                        messages.error(request, "Invalid method selected.")
                        logger.warning(f"Invalid method ID: {method_id}")
                        return redirect('view_tests')

                # ✅ Save valid data
                updated_test = form.save(commit=False)
                updated_test.lab = lab
                updated_test.status = True
                updated_test.methods = method
                updated_test.save()

                messages.success(request, "Test updated successfully!")
                logger.info(f"Test updated successfully - ID: {updated_test.id}, Name: {updated_test.test_name}")
                return redirect('view_tests')
            else:
                logger.warning(f"Form invalid: {form.errors}")
                messages.error(request, "Invalid form data. Please check inputs.")
                return redirect('view_tests')

        else:
            form = TestForm(instance=test)

        return render(request, 'tests/update_test.html', {'form': form, 'test': test, 'methods': methods})

    except Exception as e:
        logger.error(f"Error updating test ID {pk}: {str(e)}", exc_info=True)
        messages.error(request, "Error updating test.")
        return redirect('view_tests')
    
@login_required
def delete_test(request, pk):
    test = get_object_or_404(TestMaster, pk=pk, lab=request.user.lab)
    test.status = False
    test.save()
    messages.success(request, "Test deleted successfully!")
    logger.info(f"Test {pk} deleted")
    return redirect('view_tests')


@login_required(login_url='login')
def method_list(request):
    try:
        logger.info(f"Accessing method list - User: {request.user.username}")

        query = request.GET.get('q', '').strip()
        methods = Methods.objects.filter(lab=request.user.lab).order_by('-created_at')

        # 🔍 Search functionality
        if query:
            logger.debug(f"Searching methods with query: {query}")
            methods = methods.filter(
                Q(method_name__icontains=query) |
                Q(formula__icontains=query) |
                Q(method_description__icontains=query)
            )

        # 📄 Pagination setup (10 items per page)
        paginator = Paginator(methods, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        logger.debug(f"Found {methods.count()} methods matching search")
        return render(request, 'tests/method_list.html', {
            'methods': page_obj,
            'query': query,
        })

    except Exception as e:
        logger.error(f"Error fetching method list: {str(e)}", exc_info=True)
        messages.error(request, "Error fetching method list. Please try again.")
        return redirect('dashboard')

@login_required
def method_add(request):
    try:
        logger.info(f"User '{request.user.username}' adding new method.")
        if request.method == 'POST':
            method_name = request.POST.get('method_name', '').strip()
            formula = request.POST.get('formula', '').strip()
            method_description = request.POST.get('method_description', '').strip()

            if not method_name:
                messages.error(request, "Method name cannot be empty.")
                logger.warning("Method creation failed: Empty name.")
                return redirect('method_list')

            if Methods.objects.filter(method_name__iexact=method_name, lab=request.user.lab, status=True).exists():
                messages.error(request, "This method already exists.")
                logger.warning(f"Duplicate method: {method_name}")
                return redirect('method_list')

            Methods.objects.create(
                method_name=method_name,
                formula=formula,
                method_description=method_description,
                lab=request.user.lab
            )
            logger.info(f"Method '{method_name}' created successfully.")
            messages.success(request, "Method added successfully!")
            return redirect('method_list')

        form = MethodForm()
        return render(request, 'tests/method_form.html', {'form': form, 'title': 'Add Method'})
    except Exception as e:
        logger.error(f"Error adding method: {str(e)}", exc_info=True)
        messages.error(request, "Error adding method.")
        return redirect('method_list')

@login_required(login_url='login')
def method_update(request, pk):
    try:
        lab = request.user.lab
        method = get_object_or_404(Methods, pk=pk, lab=lab)
        tests = TestMaster.objects.filter(lab=lab)
        
        if request.method == 'POST':
            method_name = request.POST.get('method_name', '').strip()
            formula = request.POST.get('formula', '').strip()
            method_description = request.POST.get('method_description', '').strip()

            # ✅ Validations
            if not method_name:
                messages.error(request, "Method name cannot be empty.")
                logger.warning("Validation failed: Empty method name.")
                return redirect('method_list')

            if Methods.objects.filter(method_name__iexact=method_name, lab=lab, status=True).exclude(pk=pk).exists():
                messages.error(request, "A method with this name already exists.")
                logger.warning(f"Duplicate method name: {method_name}")
                return redirect('method_list')

            # ✅ Save method if valid
            method.method_name = method_name
            method.formula = formula
            method.method_description = method_description
            method.lab = lab
            method.save()

            messages.success(request, "Method updated successfully!")
            logger.info(f"Method updated - ID: {method.id}, Name: {method.method_name}")
            return redirect('method_list')

        else:
            form = MethodForm(instance=method)

        return render(request, 'tests/method_update.html', {'form': form, 'method': method, 'tests': tests})

    except Exception as e:
        logger.error(f"Error updating method ID {pk}: {str(e)}", exc_info=True)
        messages.error(request, "Error updating method.")
        return redirect('method_list')
    
@login_required(login_url='login')
def method_delete(request, pk):
    method = get_object_or_404(Methods, pk=pk, lab=request.user.lab)
    method.status = False
    method.save()
    logger.info(f"Method deleted - ID: {method.id}, Name: {method.method_name}")
    messages.success(request, "Method deleted successfully!")
    return redirect('method_list')


@csrf_exempt
def add_test_ajax(request):
    try:
        logger.info(f"Adding test via AJAX - User: {request.user.username}")
        if request.method == "POST":
            test_name = request.POST.get("test_name")
            test_group_id = request.POST.get("test_group")
            methods_id = request.POST.get("methods")
            lower = request.POST.get("lower_range") or None
            upper = request.POST.get("upper_range") or None
            units = request.POST.get("units")
            cost = request.POST.get("cost") or 0
            notes = request.POST.get("notes")

            test_group = TestGroupMaster.objects.filter(pk=test_group_id).first() if test_group_id else None
            method = Methods.objects.filter(pk=methods_id).first() if methods_id else None
            lab = request.user.lab  # Make sure your User model has a 'lab' field
            test = TestMaster.objects.create(
                test_name=test_name,
                test_group=test_group,
                methods=method,
                lower_range=lower,
                upper_range=upper,
                units=units,
                cost=cost,
                notes=notes,
                lab=lab,  # add this
            )
            logger.info(f"Test created via AJAX - ID: {test.test_id}")
            messages.success(request, f"{test.test_id} - {test.test_name} added successfully  !" )
            return JsonResponse({
                "success": True,
                "test_id": test.test_id,
                "test_name": test.test_name,
                "test_group": test.test_group.group_name if test.test_group else "",
                "method": test.methods.method_name if test.methods else "",
                "normal_range": f"{test.lower_range or ''} - {test.upper_range or ''}",
                "units": test.units or '',
                "cost": test.cost or 0,
                
            })
    except Exception as e:
        logger.error(f"AJAX test creation failed: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
def update_test_ajax(request, test_id):
    try:
        logger.info(f"Updating test {test_id} via AJAX - User: {request.user.username}")
        if request.method == "POST":
            test = TestMaster.objects.get(pk=test_id)

            test.test_name = request.POST.get("test_name", test.test_name)
            test.units = request.POST.get("units", test.units)
            test.cost = request.POST.get("cost", test.cost)
            test.notes = request.POST.get("notes", test.notes)

            # ✅ Handle range fields correctly
            lower = request.POST.get("lower_range")
            upper = request.POST.get("upper_range")
            if lower is not None:
                test.lower_range = lower
            if upper is not None:
                test.upper_range = upper

            test.save()
            logger.info(f"Test {test_id} updated successfully via AJAX")
            # messages.success(request, f"{test_id} - { test.test_name} updated successfully  !" )
            return JsonResponse({"success": True})
    except TestMaster.DoesNotExist:
        logger.error(f"Test {test_id} not found")
        return JsonResponse({"success": False, "error": "Test not found"})
    except Exception as e:
        logger.error(f"Error updating test {test_id}: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "error": "Invalid request"})



@csrf_exempt
def update_test_compulsory(request):
    if request.method == "POST":
        try:
            test_id = request.POST.get('test_id')
            compulsory = request.POST.get('compulsory') == 'true'
            print("test_id:", test_id, "compulsory:", compulsory)
            
            test = TestMaster.objects.get(test_id=test_id)
            test.compulsory = compulsory
            test.save()
            
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            print("Error:", e)
            traceback.print_exc()
            return JsonResponse({'status':'error','message':str(e)})
    return JsonResponse({'status':'error','message':'Invalid request'})


def get_tests(request, group_id):
    tests = TestMaster.objects.filter(test_group_id=group_id).values(
        "id", "test_name", "lower_range", "upper_range", "units", "cost", "compulsory"
    )
    test_list = []
    for t in tests:
        test_list.append({
            "test_id": t["id"],
            "test_name": t["test_name"],
            "normal_range": f"{t['lower_range']}-{t['upper_range']}" if t["lower_range"] and t["upper_range"] else "-",
            "units": t["units"],
            "cost": t["cost"],
            "compulsory": t["compulsory"],
        })
    return JsonResponse(test_list, safe=False)


def get_all_tests(request):
    tests = TestMaster.objects.all().values(
        "id", "test_name", "lower_range", "upper_range", "units", "cost", "compulsory"
    )
    test_list = []
    for t in tests:
        test_list.append({
            "test_id": t["id"],
            "test_name": t["test_name"],
            "normal_range": f"{t['lower_range']}-{t['upper_range']}" if t["lower_range"] and t["upper_range"] else "-",
            "units": t["units"],
            "cost": t["cost"],
            "compulsory": t["compulsory"],
        })
    return JsonResponse(test_list, safe=False)
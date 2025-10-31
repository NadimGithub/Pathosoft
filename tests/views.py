from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Methods, TestMaster, TestGroupMaster
from .forms import MethodForm, TestForm, TestGroupForm
from django.core.paginator import Paginator
from django.db.models import Q

# ---------- TEST GROUP ----------
@login_required
def add_test_group(request):
    lab = request.user.lab
    if request.method == 'POST':
        form = TestGroupForm(request.POST)
        if form.is_valid():
            test_group = form.save(commit=False)
            test_group.lab = lab
            test_group.save()
            return redirect('view_test_groups')
    else:
        form = TestGroupForm()
    return render(request, 'tests/add_test_group.html', {'form': form})

@login_required(login_url='login')
def view_test_groups(request):
    lab = request.user.lab
    query = request.GET.get('q', '').strip()
    groups = TestGroupMaster.objects.filter(lab=lab).order_by('id')

    if query:
        groups = groups.filter(
            Q(group_name__icontains=query)
        )

    paginator = Paginator(groups, 10)  # show 5 per page
    page_number = request.GET.get('page')
    groups_page = paginator.get_page(page_number)

    return render(request, 'tests/view_test_groups.html', {
        'groups': groups_page,
        'query': query,
    })

@login_required
def update_test_group(request, pk):
    group = get_object_or_404(TestGroupMaster, pk=pk)
    if request.method == 'POST':
        form = TestGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('view_test_groups')
    else:
        form = TestGroupForm(instance=group)
    return render(request, 'tests/update_testgroup.html', {'form': form})

@login_required
def delete_test_group(request, pk):
    group = get_object_or_404(TestGroupMaster, pk=pk)
    group.delete()
    return redirect('view_test_groups')


# ---------- TEST MASTER ----------
@login_required
def add_test(request):
    lab = request.user.lab  # current user's lab

    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.lab = lab
            test.status = True

            # Get method ID from the form
            method_id = request.POST.get('methods')

            # Assign method only if user selected one
            if method_id:
                method = get_object_or_404(Methods, pk=method_id, lab=lab)
                test.methods = method

            test.save()
            return redirect('view_tests')

    else:
        form = TestForm()

    # Fetch methods for dropdown
    methods = Methods.objects.filter(lab=lab, status=True)

    return render(request, 'tests/add_test.html', {'form': form, 'methods': methods})


@login_required(login_url='login')
def view_tests(request):
    query = request.GET.get('q', '').strip()
    
    # Fetch tests related to logged-in user's lab
    tests = TestMaster.objects.filter(lab=request.user.lab).order_by('test_id')

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



# @login_required
# def view_tests(request):
#     tests = TestMaster.objects.filter(lab=request.user.lab)
#     print(tests)
#     return render(request, 'tests/view_tests.html', {'tests': tests})

@login_required(login_url='login')
def update_test(request, pk):
    # ✅ Get the specific test for the logged-in lab
    lab = request.user.lab
    test = get_object_or_404(TestMaster, pk=pk, lab=lab)
    methods = Methods.objects.filter(lab=lab)

    # ✅ Handle form submission
    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form = form.save(commit=False)
            form.lab = lab  # Ensure lab is set correctly
            form.status = True
            method_id = request.POST.get('methods')
            method = get_object_or_404(Methods, pk=method_id, lab=lab)
            print("method_id:", method_id)
            if method_id:
                form.methods = method
            form.save()
           
            return redirect('view_tests')
    else:
        form = TestForm(instance=test)

    # ✅ Render template with both form and test (for prefilled fields)
    return render(request, 'tests/update_test.html', {'form': form, 'test': test, 'methods': methods})

@login_required
def delete_test(request, pk):
    test = get_object_or_404(TestMaster, pk=pk, lab=request.user.lab)
    test.delete()
    return redirect('view_tests')


@login_required
def method_list(request):
    methods = Methods.objects.filter(lab=request.user.lab)
    return render(request, 'tests/method_list.html', {'methods': methods})

@login_required
def method_add(request):
    if request.method == 'POST':
        form = MethodForm(request.POST)
        if form.is_valid():
            method = form.save(commit=False)
            method.created_by = request.user
            method.lab = request.user.lab
            method.save()
            return redirect('method_list')
    else:
        form = MethodForm()
    return render(request, 'tests/method_form.html', {'form': form, 'title': 'Add Method'})

@login_required
def method_update(request, pk):
    method = get_object_or_404(Methods, pk=pk, lab=request.user.lab)
    tests = TestMaster.objects.filter(lab=request.user.lab) 
    if request.method == 'POST':
        form = MethodForm(request.POST, instance=method)
        if form.is_valid():
            form.save()
            return redirect('method_list')
    else:
        form = MethodForm(instance=method)
    return render(request, 'tests/method_update.html', {'form': form, 'method': method, 'tests': tests})

@login_required
def method_delete(request, pk):
    method = get_object_or_404(Methods, pk=pk, lab=request.user.lab)
    method.delete()
    return redirect('method_list')
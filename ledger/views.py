from django.shortcuts import render
from .models import Ledger
from patient.models import PatientMaster
from doctor.models import Doctor
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import Ledger
from .forms import LedgerForm
from .models import Lab
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ledger
from .forms import LedgerForm
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
@login_required(login_url='login')
def add_ledger(request):
    # Preload foreign key dropdown data
    labs = Lab.objects.all().order_by('lab_name')
    patients = PatientMaster.objects.all().order_by('patient_name')
    doctors = Doctor.objects.all().order_by('doctor_name')

    if request.method == "POST":
        form = LedgerForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)

            # ✅ If user has lab assigned, auto-link it
            if hasattr(request.user, 'lab'):
                entry.lab = request.user.lab
            else:
                # fallback if not linked
                entry.lab = form.cleaned_data.get('lab')

            entry.save()
            return redirect('view_ledger')
    else:
        form = LedgerForm()

    context = {
        'form': form,
        'labs': labs,
        'patients': patients,
        'doctors': doctors,
    }
    return render(request, 'ledger/add_ledger.html', context)




@login_required(login_url='login')
def view_ledger(request):
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('filter', '')  # get selected filter (patient/doctor)

    # Fetch ledgers belonging to the logged-in user's lab
    ledgers = Ledger.objects.filter(lab=request.user.lab).order_by('-date')

    # ✅ Apply filter based on dropdown selection
    if filter_type == 'patient':
        ledgers = ledgers.filter(patient__isnull=False)
    elif filter_type == 'doctor':
        ledgers = ledgers.filter(doctor__isnull=False)

    # ✅ Search filter
    if query:
        search_filter = (
            Q(party_type__icontains=query) |
            Q(transaction_type__icontains=query) |
            Q(description__icontains=query) |
            Q(amount__icontains=query) |
            Q(balance_after__icontains=query)
        )

        # Apply name-based search according to dropdown filter
        if filter_type == 'patient':
            search_filter |= Q(patient__patient_name__icontains=query)
        elif filter_type == 'doctor':
            search_filter |= Q(doctor__doctor_name__icontains=query)
        else:
            search_filter |= (
                Q(patient__patient_name__icontains=query) |
                Q(doctor__doctor_name__icontains=query)
            )

        ledgers = ledgers.filter(search_filter)

    # ✅ Pagination
    paginator = Paginator(ledgers, 2)
    page_number = request.GET.get('page')
    ledgers_page = paginator.get_page(page_number)

    return render(request, 'ledger/view_ledger.html', {
        'ledgers': ledgers_page,
        'query': query,
        'filter_type': filter_type
    })

@login_required
def update_ledger(request, pk):
    ledger = get_object_or_404(Ledger, pk=pk, lab=request.user.lab)
    if request.method == "POST":
        form = LedgerForm(request.POST, instance=ledger)
        if form.is_valid():
            form.save()
            return redirect('view_ledger')
    else:
        form = LedgerForm(instance=ledger)
    return render(request, 'ledger/update_ledger.html', {'form': form})

@login_required
def delete_ledger(request, pk):
    ledger = get_object_or_404(Ledger, pk=pk, lab=request.user.lab)
    ledger.delete()
    return redirect('view_ledger')


@login_required
def ledger_home(request):
    party_type = request.GET.get('party_type', 'patient')
    selected_id = request.GET.get('id')

    if party_type == 'patient':
        parties = PatientMaster.objects.all()
        ledger_entries = Ledger.objects.filter(party_type='patient')
        if selected_id:
            ledger_entries = ledger_entries.filter(patient_id=selected_id)
    else:
        parties = Doctor.objects.all()
        ledger_entries = Ledger.objects.filter(party_type='doctor')
        if selected_id:
            ledger_entries = ledger_entries.filter(doctor_id=selected_id)

    total_credit = sum(l.amount for l in ledger_entries.filter(transaction_type='credit'))
    total_debit = sum(l.amount for l in ledger_entries.filter(transaction_type='debit'))
    balance = total_credit - total_debit

    return render(request, 'ledger/ledger_home.html', {
        'party_type': party_type,
        'parties': parties,
        'ledger_entries': ledger_entries,
        'total_credit': total_credit,
        'total_debit': total_debit,
        'balance': balance,
    })

from django.contrib import admin
from .models import Ledger

@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = ('party_type', 'patient', 'doctor', 'transaction_type', 'amount', 'date', 'balance_after')
    list_filter = ('party_type', 'transaction_type', 'date')
    search_fields = ('patient__patient_name', 'doctor__doctor_name')

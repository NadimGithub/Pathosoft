from django import forms
from .models import Ledger

class LedgerForm(forms.ModelForm):
    class Meta:
        model = Ledger
        fields = ['party_type', 'patient', 'doctor', 'transaction_type', 'amount', 'description']
        widgets = {
            'party_type': forms.Select(attrs={'class': 'form-select'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        party_type = cleaned_data.get('party_type')
        patient = cleaned_data.get('patient')
        doctor = cleaned_data.get('doctor')

        if party_type == 'patient' and not patient:
            raise forms.ValidationError("Please select a patient for Patient type.")
        if party_type == 'doctor' and not doctor:
            raise forms.ValidationError("Please select a doctor for Doctor type.")
        return cleaned_data

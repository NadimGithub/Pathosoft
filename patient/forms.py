from django import forms
from .models import PatientMaster, PatientTest

class PatientForm(forms.ModelForm):
    class Meta:
        model = PatientMaster
        fields = [
            'title', 'patient_name', 'gender', 'age', 'mobile_number',
            'doctor', 'sample_date', 'reporting_date', 'weight','blood_group','address',
            'basic_amount', 'extra_cost', 'discount',
            'total_amount', 'paid_amount', 'balance_amount', 'lab'
        ]
        widgets = {
            'sample_date': forms.DateInput(attrs={'type': 'date'}),
            'reporting_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PatientTestForm(forms.ModelForm):
    class Meta:
        model = PatientTest
        fields = ['test', 'cost']

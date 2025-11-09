import re
from django import forms
from .models import Doctor, DoctorTransaction
from decimal import Decimal
from django.core.exceptions import ValidationError


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['doctor_name', 'hospital_name', 'mobile_number', 'email', 'address', 'commission_percent']

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get("mobile_number")
        lab = self.initial.get("lab")

        # ✅ Regex validation — must be exactly 10 digits
        if not re.fullmatch(r'^[0-9]{10}$', mobile or ""):
            raise ValidationError("Enter a valid 10-digit mobile number.")

        # ✅ Check duplicate within same lab
        if Doctor.objects.filter(mobile_number=mobile, lab=lab).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This mobile number is already registered in your lab.")

        return mobile

    def clean_commission_percent(self):
        commission = self.cleaned_data.get("commission_percent", Decimal("0"))
        if commission < 0 or commission > 100:
            raise ValidationError("Commission percent must be between 0 and 100.")
        return commission

class DoctorTransactionForm(forms.ModelForm):
    class Meta:
        model = DoctorTransaction
        fields = ["amount_paid", "payment_mode", "remarks"]

    
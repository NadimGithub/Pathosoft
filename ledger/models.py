from django.db import models
from decimal import Decimal
from labs.models import Lab
from patient.models import PatientMaster
from doctor.models import Doctor

class Ledger(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('credit', 'Credit'),   # Money received
        ('debit', 'Debit'),     # Money paid
    ]

    PARTY_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]

    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPE_CHOICES)
    patient = models.ForeignKey(PatientMaster, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        """Auto update balance depending on transaction type."""
        if self.party_type == 'patient' and self.patient:
            self._update_patient_balance()
        elif self.party_type == 'doctor' and self.doctor:
            self._update_doctor_balance()
        super().save(*args, **kwargs)

    def _update_patient_balance(self):
        # Calculate new balance
        if self.transaction_type == 'credit':  # Money received from patient
            self.patient.paid_amount += self.amount
            self.patient.balance_amount -= self.amount
        elif self.transaction_type == 'debit':  # Refund to patient
            self.patient.paid_amount -= self.amount
            self.patient.balance_amount += self.amount

        # Save patient and record balance
        self.patient.save()
        self.balance_after = self.patient.balance_amount

    def _update_doctor_balance(self):
        # For doctor commission: debit = paid to doctor, credit = reverse
        from doctor.models import DoctorCommission
        commission_balance = DoctorCommission.objects.filter(
            doctor=self.doctor, is_paid=False
        ).aggregate(models.Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')

        if self.transaction_type == 'debit':
            commission_balance -= self.amount  # amount paid to doctor reduces pending
        elif self.transaction_type == 'credit':
            commission_balance += self.amount  # reversed payment

        self.balance_after = commission_balance

    def __str__(self):
        if self.party_type == 'patient' and self.patient:
            return f"Patient: {self.patient.patient_name} ({self.transaction_type} ₹{self.amount})"
        elif self.party_type == 'doctor' and self.doctor:
            return f"Doctor: {self.doctor.doctor_name} ({self.transaction_type} ₹{self.amount})"
        return "Ledger Entry"

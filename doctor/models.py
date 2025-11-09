from django.db import models
from decimal import Decimal
from labs.models import Lab


class Doctor(models.Model):
    doctor_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
     
    def __str__(self):
        return self.doctor_name


# ✅ Commission for each patient
# class DoctorCommission(models.Model):
#     doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#     patient = models.ForeignKey("patient.PatientMaster", on_delete=models.CASCADE)
#     commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
#     commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
#     is_paid = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.doctor.doctor_name} - {self.patient.patient_name}"


# ✅ Doctor Ledger to track total, paid, and balance
class DoctorLedger(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE)
    total_commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def update_balance(self):
        self.balance_amount = self.total_commission - self.paid_amount
        self.save()

    def __str__(self):
        return f"Ledger for {self.doctor.doctor_name}"


# ✅ Doctor Transaction (payments to doctors)
class DoctorTransaction(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(
        max_length=50,
        choices=[("cash", "Cash"), ("bank", "Bank Transfer"), ("upi", "UPI")],
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.doctor.doctor_name} - ₹{self.amount_paid}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ledger, _ = DoctorLedger.objects.get_or_create(doctor=self.doctor)
        ledger.paid_amount += Decimal(self.amount_paid)
        ledger.update_balance()

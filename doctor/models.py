from django.db import models

from labs.models import Lab


class Doctor(models.Model):
    doctor_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.doctor_name
    
class DoctorCommission(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey("patient.PatientMaster", on_delete=models.CASCADE)  # ✅ string reference
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor.doctor_name} - {self.patient.patient_name}"
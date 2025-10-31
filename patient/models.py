from django.db import models
from doctor.models import Doctor
from tests.models import TestMaster
from labs.models import Lab

class PatientMaster(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    patient_id = models.AutoField(primary_key=True)
    patient_name = models.CharField(max_length=100)
    title = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    mobile_number = models.CharField(max_length=15)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    sample_date = models.DateField()
    reporting_date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, null=True, blank=True)

    # Billing related fields
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient_name} ({self.patient_id})"


class PatientTest(models.Model):
    patient = models.ForeignKey(PatientMaster, on_delete=models.CASCADE, related_name='tests')
    test = models.ForeignKey(TestMaster, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

     # Add fields for report entry
    result_value = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.patient.patient_name} - {self.test.test_name}"


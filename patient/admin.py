from django.contrib import admin
from .models import PatientMaster, PatientTest,DoctorCommission

admin.site.register(PatientTest)
admin.site.register(PatientMaster)
admin.site.register(DoctorCommission)
# Register your models here.

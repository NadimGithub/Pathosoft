from django.contrib import admin
from .models import PatientMaster, PatientTest

admin.site.register(PatientTest)
admin.site.register(PatientMaster)
# Register your models here.

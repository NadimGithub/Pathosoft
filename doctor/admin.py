from django.contrib import admin
from .models import Doctor,DoctorLedger,DoctorTransaction


# admin.site.register(DoctorCommission)
admin.site.register(Doctor)
admin.site.register(DoctorLedger)
admin.site.register(DoctorTransaction)
# Register your models here



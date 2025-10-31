from django.contrib import admin
from .models import Lab

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('lab_id', 'lab_name', 'email', 'contact_no', 'status', 'created_date')
    search_fields = ('lab_name', 'lab_id', 'email')
    list_filter = ('status',)

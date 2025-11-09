from django.contrib import admin
from .models import TestMaster, TestGroupMaster, TestDepartmentMaster
admin.site.register(TestMaster)
admin.site.register(TestGroupMaster)
admin.site.register(TestDepartmentMaster)

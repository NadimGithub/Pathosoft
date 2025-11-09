from django.db import models
from labs.models import Lab

class TestDepartmentMaster(models.Model):
    dept_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.department_name

class TestGroupMaster(models.Model):
    group_name = models.CharField(max_length=100)
    department = models.ForeignKey(TestDepartmentMaster, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)


    def __str__(self):
        return self.group_name


class TestMaster(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=100)
    test_group = models.ForeignKey(TestGroupMaster, on_delete=models.CASCADE)
    methods = models.ForeignKey('Methods', on_delete=models.CASCADE, blank=True, null=True)
    # normal_range = models.CharField(max_length=100, blank=True, null=True)
    units = models.CharField(max_length=50, blank=True, null=True)
    # default_value = models.CharField(max_length=50, blank=True, null=True)
    lower_range = models.CharField(max_length=10, blank=True, null=True)
    upper_range = models.CharField(max_length=10, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    compulsory = models.BooleanField(default=False)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.test_name

class Methods(models.Model):
    method_id = models.AutoField(primary_key=True)
    method_name = models.CharField(max_length=150)
    formula = models.CharField(max_length=255, blank=True, null=True)
    method_description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # test = models.ForeignKey(TestMaster, on_delete=models.CASCADE, null=True, blank=True)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.method_name 
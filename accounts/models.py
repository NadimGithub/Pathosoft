from django.contrib.auth.models import AbstractUser
from django.db import models
from labs.models import Lab

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('lab_technician', 'Lab Technician'),
        ('lab_admin', 'Lab Administrator'),
    )

    full_name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    lab = models.ForeignKey(Lab, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lab_technician')  # 👈 added

    def __str__(self):
        return self.username

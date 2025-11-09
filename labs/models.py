from django.db import models
from django.utils import timezone

class Lab(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    lab_id = models.AutoField(primary_key=True)
    lab_name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField()
    contact_no = models.CharField(max_length=15)
    created_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.lab_name} ({self.lab_id})"

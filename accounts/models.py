from django.contrib.auth.models import AbstractUser
from django.db import models
from labs.models import Lab
from PIL import Image
from django.conf import settings
import os

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('lab_technician', 'Lab Technician'),
        ('lab_admin', 'Lab Administrator'),
    )

    full_name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15, blank=True, null=True)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lab_technician')  # 👈 added
    qualification = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True) 
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        self.email = self.email.lower()
        super().save(*args, **kwargs)


         # 🖼 Crop and resize profile image to 1:1 DP format
        if self.profile_image:
            image_path = self.profile_image.path

            try:
                img = Image.open(image_path)
                width, height = img.size

                # Determine the smaller dimension to make it square
                min_dim = min(width, height)
                left = (width - min_dim) / 2
                top = (height - min_dim) / 2
                right = (width + min_dim) / 2
                bottom = (height + min_dim) / 2

                # Crop the center square
                img = img.crop((left, top, right, bottom))

                # Optional: Resize to a standard DP size (e.g., 300x300)
                img = img.resize((300, 300), Image.LANCZOS)

                # Save it back to the same file path
                img.save(image_path)

            except Exception as e:
                print(f"Image processing failed: {e}")

            
    @property
    def display_image(self):
        """Return uploaded image if it exists, otherwise default static image."""
        if self.profile_image and self.profile_image.name:
            image_path = os.path.join(settings.MEDIA_ROOT, self.profile_image.name)
            if os.path.exists(image_path):
                return self.profile_image.url
        return settings.STATIC_URL + 'images/nadimdp.jpg'
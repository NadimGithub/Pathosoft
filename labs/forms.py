from django import forms
from .models import Lab

class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ['lab_name', 'address', 'email', 'contact_no']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

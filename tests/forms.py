from django import forms
from .models import TestDepartmentMaster, TestMaster, TestGroupMaster, Methods

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = TestDepartmentMaster
        fields = ['department_name']
        widgets = {
            'department_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Department Name'}),
            'lab': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
class TestGroupForm(forms.ModelForm):
    class Meta:
        model = TestGroupMaster
        fields = ['group_name', 'department']
        widgets = {
            'group_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Group Name'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }


class TestForm(forms.ModelForm):
    class Meta:
        model = TestMaster
        fields = ['test_name', 'test_group', 'methods', 'lower_range', 'upper_range', 'units', 'cost', 'notes']



class MethodForm(forms.ModelForm):
    class Meta:
        model = Methods
        fields = ['method_name', 'formula', 'method_description']
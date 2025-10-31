from django import forms
from .models import TestMaster, TestGroupMaster, Methods

class TestGroupForm(forms.ModelForm):
    class Meta:
        model = TestGroupMaster
        fields = ['group_name']


class TestForm(forms.ModelForm):
    class Meta:
        model = TestMaster
        fields = ['test_name', 'test_group', 'methods', 'lower_range', 'upper_range', 'units', 'cost', 'notes']



class MethodForm(forms.ModelForm):
    class Meta:
        model = Methods
        fields = ['method_name', 'formula', 'method_description']
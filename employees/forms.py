"""
Employee Forms
"""
from django import forms
from .models import Employee, Department, Designation

class EmployeeRegistrationForm(forms.ModelForm):
    """Form for registering new employees"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'department',
            'designation',
            'date_of_joining',
            'status',
            'face_image',
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EMP001'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'face_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
"""
Employee Forms - Multi-Tenant Aware
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

    def __init__(self, user, *args, **kwargs):
        """
        Initialize form with the logged-in user to filter querysets
        """
        super(EmployeeRegistrationForm, self).__init__(*args, **kwargs)
        self.user = user
        
        # Filter ForeignKeys to only show data from the user's company
        if self.user.company:
            self.fields['department'].queryset = Department.objects.filter(company=self.user.company)
            self.fields['designation'].queryset = Designation.objects.filter(company=self.user.company)
        else:
            # Fallback for superusers without company (optional)
            self.fields['department'].queryset = Department.objects.none()
            self.fields['designation'].queryset = Designation.objects.none()

    def save(self, commit=True):
        """
        Auto-assign the company from the logged-in user
        """
        employee = super(EmployeeRegistrationForm, self).save(commit=False)
        employee.company = self.user.company
        if commit:
            employee.save()
        return employee
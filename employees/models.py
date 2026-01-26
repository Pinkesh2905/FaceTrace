"""
Employee Models - Multi-Tenant Isolation
"""
from django.db import models
from django.core.validators import RegexValidator
from accounts.models import Company

class Department(models.Model):
    """Company-specific Departments"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'departments'
        unique_together = ['company', 'code'] # Code only needs to be unique within the company
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.company.name})"

class Designation(models.Model):
    """Company-specific Designations"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='designations')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'designations'
        unique_together = ['company', 'code']
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    """
    The Passive Entity.
    Identified by Face, belongs to a Company.
    Does NOT have a User account.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    # Tenancy
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    
    employee_id = models.CharField(
        max_length=20, 
        validators=[RegexValidator(r'^[A-Z0-9]+$', 'Only uppercase letters and numbers allowed')]
    )
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField() # Not unique globally anymore, only unique per company ideally
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, related_name='employees')
    
    date_of_joining = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Face recognition data
    face_image = models.ImageField(upload_to='faces/', blank=True, null=True)
    face_encoding_path = models.CharField(max_length=255, blank=True, null=True)
    is_face_registered = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        ordering = ['-created_at']
        unique_together = ['company', 'employee_id'] # ID must be unique ONLY within the company
        indexes = [
            models.Index(fields=['company', 'employee_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.first_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_encoding_filename(self):
        # Namespace encodings by company ID to prevent collisions
        return f"face_encodings/{self.company.id}/{self.employee_id}.npy"
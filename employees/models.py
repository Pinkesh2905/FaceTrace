"""
Employee Master Models
"""
from django.db import models
from django.core.validators import RegexValidator
import os

class Department(models.Model):
    """Organization departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Designation(models.Model):
    """Employee designations/positions"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'designations'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    """Main employee model with face data"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    employee_id = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9]+$', 'Only uppercase letters and numbers allowed')]
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
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
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_encoding_filename(self):
        """Generate encoding file path"""
        return f"face_encodings/{self.employee_id}.npy"
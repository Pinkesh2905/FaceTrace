"""
Camera Models - Multi-Tenant Isolation
"""
from django.db import models
from accounts.models import Company

class Location(models.Model):
    """Physical locations (e.g., Gate 1, Floor 2) within a Company"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'locations'
        unique_together = ['company', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.company.name})"

class Camera(models.Model):
    """Camera configuration for a specific Company"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cameras')
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='cameras')
    
    # Camera source (0 for webcam, URL for IP camera, etc.)
    stream_source = models.CharField(max_length=255, default='0', help_text='0 for webcam, or camera stream URL')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_primary = models.BooleanField(default=False, help_text='Primary camera for attendance')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cameras'
        ordering = ['-is_primary', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.location.name}"
    
    def get_stream_source_int(self):
        try:
            return int(self.stream_source)
        except ValueError:
            return self.stream_source
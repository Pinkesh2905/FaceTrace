"""
Camera Management Models
"""
from django.db import models

class Location(models.Model):
    """Physical locations where cameras are installed"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'locations'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Camera(models.Model):
    """Camera configuration"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
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
        """Convert stream source to int if it's a number, else return as is"""
        try:
            return int(self.stream_source)
        except ValueError:
            return self.stream_source
"""
Attendance Models
"""
from django.db import models
from employees.models import Employee
from cameras.models import Camera

class AttendanceRecord(models.Model):
    """Individual attendance punch records"""
    TYPE_CHOICES = [
        ('IN', 'Check In'),
        ('OUT', 'Check Out'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, related_name='attendance_records')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    punch_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    
    # Face recognition metadata
    confidence_score = models.FloatField(help_text='Recognition confidence (0-100)')
    face_distance = models.FloatField(help_text='Face encoding distance')
    
    # Optional: snapshot of detected face
    snapshot = models.ImageField(upload_to='attendance_snapshots/', blank=True, null=True)
    
    is_manual = models.BooleanField(default=False, help_text='Manually marked by admin')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'attendance_records'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.punch_type} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class DailyAttendanceSummary(models.Model):
    """Daily summary of employee attendance"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField()
    
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    is_present = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    is_early_departure = models.BooleanField(default=False)
    
    first_punch = models.ForeignKey(
        AttendanceRecord, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='daily_first_punch'
    )
    last_punch = models.ForeignKey(
        AttendanceRecord, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='daily_last_punch'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_attendance_summary'
        ordering = ['-date']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['employee', 'date']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"
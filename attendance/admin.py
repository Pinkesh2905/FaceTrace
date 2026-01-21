"""
Attendance Admin Configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AttendanceRecord, DailyAttendanceSummary

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'punch_type',
        'timestamp',
        'camera',
        'confidence_display',
        'is_manual'
    )
    list_filter = ('punch_type', 'is_manual', 'camera', 'timestamp')
    search_fields = ('employee__employee_id', 'employee__first_name', 'employee__last_name')
    readonly_fields = ('timestamp', 'confidence_score', 'face_distance')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Attendance Info', {
            'fields': ('employee', 'punch_type', 'timestamp', 'camera')
        }),
        ('Recognition Data', {
            'fields': ('confidence_score', 'face_distance', 'snapshot')
        }),
        ('Manual Entry', {
            'fields': ('is_manual', 'notes')
        }),
    )
    
    def confidence_display(self, obj):
        color = 'green' if obj.confidence_score >= 80 else 'orange' if obj.confidence_score >= 60 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            obj.confidence_score
        )
    confidence_display.short_description = 'Confidence'

@admin.register(DailyAttendanceSummary)
class DailyAttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'date',
        'check_in_time',
        'check_out_time',
        'total_hours',
        'status_display'
    )
    list_filter = ('date', 'is_present', 'is_late')
    search_fields = ('employee__employee_id', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    def status_display(self, obj):
        if not obj.is_present:
            return format_html('<span style="color: red;">Absent</span>')
        
        status = 'Present'
        color = 'green'
        
        if obj.is_late:
            status += ' (Late)'
            color = 'orange'
        if obj.is_early_departure:
            status += ' (Early Out)'
            color = 'orange'
        
        return format_html('<span style="color: {};">{}</span>', color, status)
    status_display.short_description = 'Status'
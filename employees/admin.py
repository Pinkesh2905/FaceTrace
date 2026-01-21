"""
Employees Admin Configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Designation, Employee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id', 
        'get_full_name', 
        'department', 
        'designation', 
        'status',
        'face_status',
        'date_of_joining'
    )
    list_filter = ('status', 'is_face_registered', 'department', 'designation')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at', 'face_image_preview')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Organization', {
            'fields': ('department', 'designation', 'date_of_joining', 'status')
        }),
        ('Face Recognition', {
            'fields': ('face_image', 'face_image_preview', 'is_face_registered', 'face_encoding_path')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def face_status(self, obj):
        if obj.is_face_registered:
            return format_html('<span style="color: green;">✓ Registered</span>')
        return format_html('<span style="color: red;">✗ Not Registered</span>')
    face_status.short_description = 'Face Status'
    
    def face_image_preview(self, obj):
        if obj.face_image:
            return format_html('<img src="{}" width="150" height="150" />', obj.face_image.url)
        return "No image"
    face_image_preview.short_description = 'Face Preview'
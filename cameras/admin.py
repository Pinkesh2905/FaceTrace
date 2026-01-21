"""
Cameras Admin Configuration
"""
from django.contrib import admin
from .models import Location, Camera

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'stream_source', 'status', 'is_primary', 'created_at')
    list_filter = ('status', 'is_primary', 'location')
    search_fields = ('name',)
    ordering = ('-is_primary', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'location', 'status', 'is_primary')
        }),
        ('Configuration', {
            'fields': ('stream_source',)
        }),
    )
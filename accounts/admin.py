"""
Accounts Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'registration_number', 'is_verified', 'is_active', 'proof_link')
    list_filter = ('is_verified', 'is_active')
    search_fields = ('name', 'contact_email', 'registration_number')
    actions = ['approve_companies']
    
    def proof_link(self, obj):
        if obj.proof_document:
            return format_html('<a href="{}" target="_blank" class="button">View Proof</a>', obj.proof_document.url)
        return "No Proof"
    proof_link.short_description = "Proof Document"

    def approve_companies(self, request, queryset):
        rows_updated = queryset.update(is_verified=True, is_active=True)
        self.message_user(request, f"{rows_updated} companies approved successfully.")
    approve_companies.short_description = "Approve selected companies"

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'company', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active', 'company')
    search_fields = ('username', 'email', 'company__name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Platform Info', {'fields': ('role', 'phone', 'company')}),
    )
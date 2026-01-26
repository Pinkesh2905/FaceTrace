"""
Account Models - Multi-Tenant Architecture
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class Company(models.Model):
    """
    The Tenant Model.
    Represents a Factory, Office, or Organization using the platform.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="Unique identifier for URL/API")
    
    # Company Metadata
    address = models.TextField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, null=True)
    
    # Verification Details
    registration_number = models.CharField(max_length=50, blank=True, help_text="Business Registration No / CIN / GST")
    proof_document = models.FileField(upload_to='company_proofs/', blank=True, null=True, help_text="Official registration document (PDF/Image)")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Is subscription active?")
    is_verified = models.BooleanField(default=False, help_text="Has admin verified documents?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    Platform Users (People who can login).
    """
    ROLE_CHOICES = [
        ('platform_admin', 'Platform Super Admin'), 
        ('employer_admin', 'Employer / Company Admin'), 
        ('manager', 'Manager'), # Can view reports
    ]
    
    # Link user to a specific company (Tenant)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='users'
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employer_admin')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        if self.company:
            return f"{self.username} ({self.company.name})"
        return f"{self.username} (Platform Admin)"
"""
Custom User Model
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
    Can be extended later with roles, permissions, etc.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('operator', 'Operator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
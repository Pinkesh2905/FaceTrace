"""
Employee URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    # Changed: Dashboard is now at /dashboard/ instead of root /
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/register/', views.employee_register, name='employee_register'),
    path('employees/<str:employee_id>/', views.employee_detail, name='employee_detail'),
    path('employees/<str:employee_id>/delete/', views.employee_delete, name='employee_delete'), # New
]
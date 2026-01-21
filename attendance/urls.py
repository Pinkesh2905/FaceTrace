"""
Attendance URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.attendance_history, name='attendance_history'),
    path('daily/', views.daily_summary, name='daily_summary'),
    path('employee/<str:employee_id>/', views.employee_attendance_detail, name='employee_attendance_detail'),
]
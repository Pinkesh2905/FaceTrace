"""
Attendance Views
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from .models import AttendanceRecord, DailyAttendanceSummary
from employees.models import Employee
from .services import AttendanceService

attendance_service = AttendanceService()

@login_required
def attendance_history(request):
    """View attendance history with filters"""
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_id = request.GET.get('employee_id')
    
    # Base queryset
    records = AttendanceRecord.objects.select_related(
        'employee', 'camera'
    ).order_by('-timestamp')
    
    # Apply filters
    if date_from:
        records = records.filter(timestamp__date__gte=date_from)
    
    if date_to:
        records = records.filter(timestamp__date__lte=date_to)
    
    if employee_id:
        records = records.filter(employee__employee_id=employee_id)
    
    # Limit results
    records = records[:100]
    
    # Get all employees for filter dropdown
    employees = Employee.objects.filter(status='active').order_by('employee_id')
    
    context = {
        'records': records,
        'employees': employees,
        'date_from': date_from,
        'date_to': date_to,
        'employee_id': employee_id,
    }
    
    return render(request, 'attendance/attendance_history.html', context)

@login_required
def daily_summary(request):
    """View daily attendance summary"""
    # Get date parameter or use today
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        # Use local date to align with timezone-aware records
        from django.utils import timezone
        selected_date = timezone.localdate()
    
    # Get summaries for the date
    summaries = DailyAttendanceSummary.objects.filter(
        date=selected_date
    ).select_related('employee', 'employee__department').order_by('employee__employee_id')
    
    # Calculate statistics
    total_employees = Employee.objects.filter(status='active').count()
    present_count = summaries.filter(is_present=True).count()
    absent_count = total_employees - present_count
    late_count = summaries.filter(is_late=True).count()
    
    context = {
        'summaries': summaries,
        'selected_date': selected_date,
        'total_employees': total_employees,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_percentage': (present_count / total_employees * 100) if total_employees > 0 else 0,
    }
    
    return render(request, 'attendance/daily_summary.html', context)

@login_required
def employee_attendance_detail(request, employee_id):
    """Detailed attendance view for a specific employee"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    # Get month and year parameters with validation
    try:
        month = int(request.GET.get('month', date.today().month))
        if month < 1 or month > 12:
            raise ValueError
    except (TypeError, ValueError):
        month = date.today().month
    
    try:
        year = int(request.GET.get('year', date.today().year))
    except (TypeError, ValueError):
        year = date.today().year
    
    # Get monthly summaries
    summaries = DailyAttendanceSummary.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    ).order_by('-date')
    
    # Get statistics
    stats = attendance_service.get_attendance_stats(employee, month, year)
    
    context = {
        'employee': employee,
        'summaries': summaries,
        'stats': stats,
        'month': month,
        'year': year,
    }
    
    return render(request, 'attendance/employee_detail.html', context)
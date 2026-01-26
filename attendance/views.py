"""
Attendance Views - Multi-Tenant Aware
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime
from .models import AttendanceRecord, DailyAttendanceSummary
from employees.models import Employee
from .services import AttendanceService

attendance_service = AttendanceService()

@login_required
def attendance_history(request):
    """View attendance history - Company Isolated"""
    if not request.user.company:
        return redirect('dashboard')

    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    employee_id = request.GET.get('employee_id')
    
    # Base queryset - Filter by Company
    records = AttendanceRecord.objects.filter(
        employee__company=request.user.company
    ).select_related(
        'employee', 'camera'
    ).order_by('-timestamp')
    
    # Apply filters
    if date_from:
        records = records.filter(timestamp__date__gte=date_from)
    
    if date_to:
        records = records.filter(timestamp__date__lte=date_to)
    
    if employee_id:
        records = records.filter(employee__employee_id=employee_id)
    
    # Limit results for performance
    records = records[:100]
    
    # Get employees for filter dropdown (Only own company)
    employees = Employee.objects.filter(
        company=request.user.company, 
        status='active'
    ).order_by('employee_id')
    
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
    """View daily attendance summary - Company Isolated"""
    if not request.user.company:
        return redirect('dashboard')

    # Get date parameter or use today
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        from django.utils import timezone
        selected_date = timezone.localdate()
    
    # Get summaries for the date (Filter by Company)
    summaries = DailyAttendanceSummary.objects.filter(
        employee__company=request.user.company,
        date=selected_date
    ).select_related('employee', 'employee__department').order_by('employee__employee_id')
    
    # Calculate statistics for THIS company
    total_employees = Employee.objects.filter(
        company=request.user.company, 
        status='active'
    ).count()
    
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
    # Ensure employee belongs to user's company
    employee = get_object_or_404(
        Employee, 
        employee_id=employee_id, 
        company=request.user.company
    )
    
    # Get month and year parameters
    try:
        month = int(request.GET.get('month', date.today().month))
        year = int(request.GET.get('year', date.today().year))
    except (TypeError, ValueError):
        month = date.today().month
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
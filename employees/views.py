"""
Employee Management Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Employee, Department, Designation
from .forms import EmployeeRegistrationForm
from recognition.encoding_manager import EncodingManager
from attendance.models import AttendanceRecord, DailyAttendanceSummary
from datetime import date

@login_required
def dashboard(request):
    """Main dashboard view"""
    today = date.today()
    
    # Statistics
    total_employees = Employee.objects.filter(status='active').count()
    face_registered = Employee.objects.filter(status='active', is_face_registered=True).count()
    
    # Today's attendance
    today_present = DailyAttendanceSummary.objects.filter(
        date=today,
        is_present=True
    ).count()
    
    # Recent attendance records
    recent_records = AttendanceRecord.objects.select_related(
        'employee', 'camera'
    ).order_by('-timestamp')[:10]
    
    # Employees without face registration
    pending_registration = Employee.objects.filter(
        status='active',
        is_face_registered=False
    )[:5]
    
    context = {
        'total_employees': total_employees,
        'face_registered': face_registered,
        'today_present': today_present,
        'recent_records': recent_records,
        'pending_registration': pending_registration,
        'registration_percentage': (face_registered / total_employees * 100) if total_employees > 0 else 0,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def employee_list(request):
    """List all employees"""
    employees = Employee.objects.select_related(
        'department', 'designation'
    ).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        employees = employees.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        employees = employees.filter(
            Q(employee_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'employees': employees,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_register(request):
    """Register new employee with face"""
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            
            # Process face image if uploaded
            if employee.face_image:
                encoding_manager = EncodingManager()
                success, error_message = encoding_manager.save_employee_encoding(
                    employee,
                    employee.face_image.path
                )
                
                if success:
                    # Keep the in-memory cache fresh for live recognition
                    encoding_manager.refresh_cache()
                    messages.success(
                        request,
                        f'Employee {employee.employee_id} registered successfully with face recognition!'
                    )
                else:
                    messages.warning(
                        request,
                        f'Employee {employee.employee_id} registered, but face could not be processed. {error_message}'
                    )
            else:
                messages.success(
                    request,
                    f'Employee {employee.employee_id} registered. Upload face image to enable recognition.'
                )
            
            return redirect('employee_list')
    else:
        form = EmployeeRegistrationForm()
    
    return render(request, 'employees/employee_register.html', {'form': form})

@login_required
def employee_detail(request, employee_id):
    """View employee details and attendance history"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    # Recent attendance
    recent_attendance = AttendanceRecord.objects.filter(
        employee=employee
    ).select_related('camera').order_by('-timestamp')[:20]
    
    # Monthly summary
    monthly_summaries = DailyAttendanceSummary.objects.filter(
        employee=employee
    ).order_by('-date')[:30]
    
    context = {
        'employee': employee,
        'recent_attendance': recent_attendance,
        'monthly_summaries': monthly_summaries,
    }
    
    return render(request, 'employees/employee_detail.html', context)
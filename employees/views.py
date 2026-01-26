"""
Employee Management Views - Multi-Tenant Aware
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.files.base import ContentFile
import base64
import os
from datetime import date

from .models import Employee, Department, Designation
from .forms import EmployeeRegistrationForm
from recognition.encoding_manager import EncodingManager
from attendance.models import AttendanceRecord, DailyAttendanceSummary

@login_required
def dashboard(request):
    """Main dashboard view - Company Isolated"""
    # Security Guard: Ensure user has a company
    if not request.user.company:
        # If user is superuser (platform admin), redirect to admin panel
        if request.user.is_superuser:
            return redirect('/admin/')
        return render(request, 'dashboard.html', {'error': 'You are not linked to any company.'})

    # VERIFICATION CHECK
    if not request.user.company.is_verified:
        return render(request, 'accounts/pending_approval.html')

    company = request.user.company
    today = date.today()
    
    # Statistics (Filtered by Company)
    total_employees = Employee.objects.filter(company=company, status='active').count()
    face_registered = Employee.objects.filter(company=company, status='active', is_face_registered=True).count()
    
    # Today's attendance (Filtered by Company via Employee)
    today_present = DailyAttendanceSummary.objects.filter(
        employee__company=company,
        date=today,
        is_present=True
    ).count()
    
    # Recent attendance records (Filtered by Company)
    recent_records = AttendanceRecord.objects.filter(
        employee__company=company
    ).select_related(
        'employee', 'camera'
    ).order_by('-timestamp')[:10]
    
    # Employees without face registration (Filtered by Company)
    pending_registration = Employee.objects.filter(
        company=company,
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
        'company_name': company.name
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def employee_list(request):
    """List all employees - Company Isolated"""
    if not request.user.company:
        return redirect('login')
        
    if not request.user.company.is_verified:
        return render(request, 'accounts/pending_approval.html')

    # Filter by Company
    employees = Employee.objects.filter(
        company=request.user.company
    ).select_related(
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
    """Register new employee - Company Isolated"""
    if not request.user.company:
        return redirect('dashboard')
        
    if not request.user.company.is_verified:
        return render(request, 'accounts/pending_approval.html')

    if request.method == 'POST':
        # Pass 'user' to form to handle company assignment and filtering
        form = EmployeeRegistrationForm(request.user, request.POST, request.FILES)
        
        if form.is_valid():
            employee = form.save(commit=False)
            
            # Check for webcam image data
            camera_image_data = request.POST.get('camera_image')
            
            if camera_image_data:
                try:
                    format_string, imgstr = camera_image_data.split(';base64,') 
                    ext = format_string.split('/')[-1]
                    file_name = f'{employee.employee_id}_face.{ext}'
                    data = ContentFile(base64.b64decode(imgstr), name=file_name)
                    employee.face_image = data
                except Exception as e:
                    messages.error(request, f"Error processing webcam image: {e}")
            
            # Save (Company is assigned inside form.save())
            employee.save()
            
            # Process face encoding
            if employee.face_image:
                encoding_manager = EncodingManager()
                success, error_message = encoding_manager.save_employee_encoding(
                    employee,
                    employee.face_image.path
                )
                
                if success:
                    # Update cache (for this company)
                    encoding_manager.refresh_cache(company_id=request.user.company.id)
                    messages.success(request, f'Employee {employee.employee_id} registered successfully!')
                else:
                    messages.warning(request, f'Registered, but face error: {error_message}')
            else:
                messages.success(request, f'Employee {employee.employee_id} registered (No Face).')
            
            return redirect('employee_list')
    else:
        # Pass 'user' to init form
        form = EmployeeRegistrationForm(user=request.user)
    
    return render(request, 'employees/employee_register.html', {'form': form})

@login_required
def employee_detail(request, employee_id):
    """View employee details - Company Isolated"""
    # Ensure we only fetch employees belonging to the user's company
    employee = get_object_or_404(
        Employee, 
        employee_id=employee_id, 
        company=request.user.company
    )
    
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

@login_required
def employee_delete(request, employee_id):
    """Delete an employee and their face data - Company Isolated"""
    if not request.user.company:
        return redirect('dashboard')
        
    employee = get_object_or_404(
        Employee, 
        employee_id=employee_id, 
        company=request.user.company
    )
    
    if request.method == 'POST':
        # 1. Delete physical face image if exists
        if employee.face_image:
            try:
                if os.path.isfile(employee.face_image.path):
                    os.remove(employee.face_image.path)
            except Exception as e:
                print(f"Error deleting image file: {e}")

        # 2. Delete encoding file if exists
        if employee.face_encoding_path:
            try:
                if os.path.isfile(employee.face_encoding_path):
                    os.remove(employee.face_encoding_path)
            except Exception as e:
                print(f"Error deleting encoding file: {e}")
                
        # 3. Delete database record
        employee.delete()
        
        # 4. Refresh Cache for this company
        encoding_manager = EncodingManager()
        encoding_manager.refresh_cache(company_id=request.user.company.id)
        
        messages.success(request, f"Employee {employee_id} deleted successfully.")
        return redirect('employee_list')
        
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})
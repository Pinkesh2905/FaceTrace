"""
Attendance Business Logic Service
"""
from datetime import datetime, date, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from .models import AttendanceRecord, DailyAttendanceSummary
from employees.models import Employee
from cameras.models import Camera

class AttendanceService:
    """
    Handles all attendance-related business logic
    """
    
    def __init__(self):
        # Configuration
        self.min_punch_interval_minutes = 5  # Minimum time between punches
        self.confidence_threshold = 70.0  # Minimum confidence for auto-attendance
        self.work_start_time = time(9, 0)  # 9:00 AM
        self.work_end_time = time(18, 0)  # 6:00 PM
    
    def mark_attendance(self, employee, confidence_score, face_distance, camera=None, is_manual=False):
        """
        Mark attendance for an employee
        
        Args:
            employee: Employee instance
            confidence_score: Recognition confidence (0-100)
            face_distance: Face encoding distance
            camera: Camera instance (optional)
            is_manual: Whether this is a manual entry
        
        Returns:
            AttendanceRecord or None
        """
        # Check if employee is active
        if employee.status != 'active':
            return None
        
        # Check confidence threshold (skip for manual entries)
        if not is_manual and confidence_score < self.confidence_threshold:
            return None
        
        now = timezone.now()
        # Use local date boundaries to avoid UTC date drift
        today = timezone.localdate()
        day_start, day_end = self._get_day_bounds(today)
        
        # Get last punch for this employee today
        last_punch = AttendanceRecord.objects.filter(
            employee=employee,
            timestamp__gte=day_start,
            timestamp__lt=day_end
        ).order_by('-timestamp').first()
        
        # Determine punch type
        if last_punch is None:
            punch_type = 'IN'
        else:
            # Check minimum interval
            time_diff = (now - last_punch.timestamp).total_seconds() / 60
            if time_diff < self.min_punch_interval_minutes:
                return None  # Too soon since last punch
            
            # Alternate between IN and OUT
            punch_type = 'OUT' if last_punch.punch_type == 'IN' else 'IN'
        
        # Create attendance record
        with transaction.atomic():
            record = AttendanceRecord.objects.create(
                employee=employee,
                camera=camera,
                punch_type=punch_type,
                confidence_score=confidence_score,
                face_distance=face_distance,
                is_manual=is_manual
            )
            
            # Update daily summary
            self.update_daily_summary(employee, today)
        
        return record
    
    def update_daily_summary(self, employee, date_obj):
        """
        Update or create daily attendance summary
        """
        day_start, day_end = self._get_day_bounds(date_obj)
        
        # Get all punches for this day
        punches = AttendanceRecord.objects.filter(
            employee=employee,
            timestamp__gte=day_start,
            timestamp__lt=day_end
        ).order_by('timestamp')
        
        if not punches.exists():
            return None
        
        # Get first IN and last OUT
        first_in = punches.filter(punch_type='IN').first()
        last_out = punches.filter(punch_type='OUT').last()
        
        # Calculate totals
        check_in_time = first_in.timestamp.time() if first_in else None
        check_out_time = last_out.timestamp.time() if last_out else None
        
        # Calculate total hours
        total_hours = None
        if first_in and last_out:
            time_diff = last_out.timestamp - first_in.timestamp
            # DailyAttendanceSummary.total_hours is a DecimalField; store a Decimal to avoid float artifacts.
            hours = Decimal(str(time_diff.total_seconds() / 3600))
            total_hours = hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Determine status flags
        is_present = first_in is not None
        is_late = False
        is_early_departure = False
        
        if check_in_time and check_in_time > self.work_start_time:
            is_late = True
        
        if check_out_time and check_out_time < self.work_end_time and last_out:
            is_early_departure = True
        
        # Update or create summary
        summary, created = DailyAttendanceSummary.objects.update_or_create(
            employee=employee,
            date=date_obj,
            defaults={
                'check_in_time': check_in_time,
                'check_out_time': check_out_time,
                'total_hours': total_hours,
                'is_present': is_present,
                'is_late': is_late,
                'is_early_departure': is_early_departure,
                'first_punch': first_in,
                'last_punch': last_out,
            }
        )
        
        return summary
    
    def _get_day_bounds(self, date_obj):
        """
        Return timezone-aware start and end for the given local date.
        """
        tz = timezone.get_current_timezone()
        start_dt = datetime.combine(date_obj, time.min)
        end_dt = datetime.combine(date_obj, time.max)
        return (
            timezone.make_aware(start_dt, tz),
            timezone.make_aware(end_dt, tz),
        )
    
    def get_employee_attendance_history(self, employee, start_date=None, end_date=None):
        """
        Get attendance history for an employee
        """
        queryset = AttendanceRecord.objects.filter(employee=employee)
        
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        
        return queryset.order_by('-timestamp')
    
    def get_daily_summary(self, employee, date_obj):
        """
        Get daily summary for an employee
        """
        try:
            return DailyAttendanceSummary.objects.get(
                employee=employee,
                date=date_obj
            )
        except DailyAttendanceSummary.DoesNotExist:
            return None
    
    def get_attendance_stats(self, employee, month=None, year=None):
        """
        Get attendance statistics for an employee
        """
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year
        
        summaries = DailyAttendanceSummary.objects.filter(
            employee=employee,
            date__month=month,
            date__year=year
        )
        
        total_days = summaries.count()
        present_days = summaries.filter(is_present=True).count()
        late_days = summaries.filter(is_late=True).count()
        early_departures = summaries.filter(is_early_departure=True).count()
        
        return {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': total_days - present_days,
            'late_days': late_days,
            'early_departures': early_departures,
            'attendance_percentage': (present_days / total_days * 100) if total_days > 0 else 0
        }
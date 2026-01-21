# FaceCognition Platform - Quick Reference

## Common Commands

### Start Development Server
```bash
python manage.py runserver
```

### Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Access Django Shell
```bash
python manage.py shell
```

---

## Project Structure Quick Map

```
FaceCognitionPlatform/
│
├── accounts/              # User management
│   ├── models.py         # Custom User model
│   └── admin.py          # User admin
│
├── employees/            # Employee master data
│   ├── models.py         # Employee, Department, Designation
│   ├── views.py          # Dashboard, registration, lists
│   ├── forms.py          # Employee forms
│   └── admin.py          # Employee admin
│
├── recognition/          # Face AI engine
│   ├── face_engine.py    # Core OpenCV + face_recognition
│   ├── encoding_manager.py # Face encoding storage
│   └── views.py          # Live feed, video stream
│
├── attendance/           # Attendance logic
│   ├── models.py         # AttendanceRecord, DailyAttendanceSummary
│   ├── services.py       # Business logic
│   ├── views.py          # History, summaries
│   └── admin.py          # Attendance admin
│
├── cameras/              # Camera configuration
│   ├── models.py         # Camera, Location
│   └── admin.py          # Camera admin
│
└── templates/            # HTML templates
    ├── base.html         # Base layout
    ├── login.html        # Login page
    ├── dashboard.html    # Main dashboard
    ├── employees/        # Employee templates
    ├── attendance/       # Attendance templates
    └── recognition/      # Recognition templates
```

---

## Key URLs

| URL | Purpose |
|-----|---------|
| `/` | Dashboard |
| `/login/` | Login page |
| `/admin/` | Django admin |
| `/employees/` | Employee list |
| `/employees/register/` | Register new employee |
| `/employees/{id}/` | Employee detail |
| `/recognition/live/` | Live face recognition |
| `/attendance/history/` | Attendance records |
| `/attendance/daily/` | Daily summary |

---

## Database Models Cheat Sheet

### Employee
```python
employee_id (CharField, unique)
first_name, last_name
email (EmailField, unique)
department (FK to Department)
designation (FK to Designation)
face_image (ImageField)
face_encoding_path (CharField)
is_face_registered (BooleanField)
status (active/inactive/suspended)
```

### AttendanceRecord
```python
employee (FK to Employee)
camera (FK to Camera)
timestamp (DateTimeField, auto)
punch_type (IN/OUT)
confidence_score (FloatField)
face_distance (FloatField)
is_manual (BooleanField)
```

### DailyAttendanceSummary
```python
employee (FK to Employee)
date (DateField)
check_in_time, check_out_time
total_hours (DecimalField)
is_present, is_late, is_early_departure
```

---

## Key Functions Reference

### FaceEngine (`recognition/face_engine.py`)
```python
detect_faces(image)                    # Find faces in image
encode_face(image, face_location)      # Generate 128D encoding
compare_faces(known, face_encoding)    # Match faces
recognize_face(encoding, known_dict)   # Identify employee
draw_face_box(frame, location, name)   # Draw on frame
```

### EncodingManager (`recognition/encoding_manager.py`)
```python
save_employee_encoding(employee, image_path)  # Save encoding
load_employee_encoding(employee_id)           # Load single
load_all_encodings()                          # Load all active
refresh_cache()                               # Reload cache
```

### AttendanceService (`attendance/services.py`)
```python
mark_attendance(employee, confidence, distance)  # Mark IN/OUT
update_daily_summary(employee, date)            # Update summary
get_attendance_stats(employee, month, year)     # Get statistics
```

---

## Configuration Settings

### `settings.py` Key Settings
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
FACE_ENCODINGS_DIR = MEDIA_ROOT / 'face_encodings'
FACE_IMAGES_DIR = MEDIA_ROOT / 'faces'
AUTH_USER_MODEL = 'accounts.User'
TIME_ZONE = 'Asia/Kolkata'  # Change as needed
```

### Face Recognition Parameters
```python
# In face_engine.py
tolerance = 0.6          # Lower = stricter (default: 0.6)
model = 'hog'            # 'hog' (fast) or 'cnn' (accurate)

# In attendance/services.py
min_punch_interval_minutes = 5    # Min time between punches
confidence_threshold = 70.0       # Min confidence for auto-mark
work_start_time = time(9, 0)      # Work start (9:00 AM)
work_end_time = time(18, 0)       # Work end (6:00 PM)
```

---

## Common Tasks

### Add Sample Data
```python
python manage.py shell

from employees.models import Department, Designation
from cameras.models import Location, Camera

# Departments
Department.objects.create(name="Engineering", code="ENG")
Department.objects.create(name="HR", code="HR")

# Designations
Designation.objects.create(name="Manager", code="MGR")
Designation.objects.create(name="Engineer", code="ENG")

# Location & Camera
loc = Location.objects.create(name="Main Office", code="MAIN")
Camera.objects.create(
    name="Entrance Camera",
    location=loc,
    stream_source="0",  # Webcam
    is_primary=True
)
```

### Test Face Recognition
```python
from recognition.face_engine import FaceEngine
import cv2

engine = FaceEngine()

# Test with image
image = cv2.imread('path/to/image.jpg')
faces = engine.detect_faces(image)
print(f"Found {len(faces)} faces")
```

### Reset Attendance Data
```python
from attendance.models import AttendanceRecord, DailyAttendanceSummary

AttendanceRecord.objects.all().delete()
DailyAttendanceSummary.objects.all().delete()
```

---

## Troubleshooting Quick Fixes

### Camera not opening
```python
# Test camera
import cv2
cap = cv2.VideoCapture(0)
print(cap.isOpened())  # Should be True
cap.release()
```

### Face not encoding
- Check image quality (min 400x400px)
- Ensure face is visible and front-facing
- Check lighting conditions
- Verify OpenCV installation: `pip install opencv-python`

### Low recognition confidence
- Re-register with better image
- Adjust tolerance in `face_engine.py`
- Check camera angle and lighting

### Migrations conflict
```bash
python manage.py migrate --fake
python manage.py makemigrations
python manage.py migrate
```

---

## Performance Tips

1. **Process every Nth frame** (already in code: process_frame % 3)
2. **Limit camera resolution** (set to 640x480 in code)
3. **Cache encodings** (done automatically)
4. **Use 'hog' model** for CPU (faster than 'cnn')
5. **Add database indexes** (already included in models)

---

## Security Checklist (Production)

- [ ] Change SECRET_KEY
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use HTTPS
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set up proper media/static serving
- [ ] Configure CORS if needed
- [ ] Set up backup system
- [ ] Add rate limiting
- [ ] Enable CSRF protection

---

## Useful Django Admin URLs

- `/admin/` - Main admin
- `/admin/employees/employee/` - Employees
- `/admin/attendance/attendancerecord/` - Attendance records
- `/admin/cameras/camera/` - Camera management

---

## File Upload Limits

| Type | Max Size | Format |
|------|----------|--------|
| Face Image | 5MB | JPG, PNG |
| Min Resolution | 400x400 | pixels |

---

## Default User Roles

- **admin**: Full access
- **manager**: View reports, manage employees
- **operator**: Basic operations only

---

This is your quick reference for the Phase 1 MVP. Keep this handy during development!
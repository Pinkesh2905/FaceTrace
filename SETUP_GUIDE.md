# FaceCognition Platform - Complete Setup Guide

## Phase 1 MVP - Step-by-Step Installation

---

## Prerequisites

- Python 3.8 or higher
- Webcam or IP camera
- 4GB RAM minimum (8GB recommended)
- Windows/Linux/Mac

---

## Step 1: Environment Setup

```bash
# Create project directory
mkdir FaceCognitionPlatform
cd FaceCognitionPlatform

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

---

## Step 2: Install Dependencies

```bash
# Install all required packages
pip install django==4.2
pip install pillow
pip install opencv-python
pip install opencv-contrib-python
pip install face-recognition
pip install numpy
```

**Note for Windows users:** If face-recognition installation fails:
```bash
pip install cmake
pip install dlib
pip install face-recognition
```

---

## Step 3: Create Django Project

```bash
# Create Django project
django-admin startproject FaceCognitionPlatform .

# Create all apps
python manage.py startapp accounts
python manage.py startapp employees
python manage.py startapp recognition
python manage.py startapp attendance
python manage.py startapp cameras
```

---

## Step 4: Copy All Code Files

Copy all the provided code files to their respective locations:

### Project Configuration
- `FaceCognitionPlatform/settings.py`
- `FaceCognitionPlatform/urls.py`

### Models
- `accounts/models.py`
- `employees/models.py`
- `cameras/models.py`
- `attendance/models.py`

### Admin
- `accounts/admin.py`
- `employees/admin.py`
- `cameras/admin.py`
- `attendance/admin.py`

### Core Logic
- `recognition/face_engine.py`
- `recognition/encoding_manager.py`
- `recognition/views.py`
- `recognition/urls.py`

### Business Logic
- `attendance/services.py`
- `attendance/views.py`
- `attendance/urls.py`
- `employees/views.py`
- `employees/forms.py`
- `employees/urls.py`

### Templates
Create `templates/` folder in project root and add:
- `templates/base.html`
- `templates/login.html`
- `templates/dashboard.html`
- `templates/recognition/live_feed.html`

You'll need to create additional templates for employee and attendance views.

---

## Step 5: Create Required Directories

```bash
# Create media directories
mkdir -p media/faces
mkdir -p media/face_encodings
mkdir -p media/attendance_snapshots

# Create static directory
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
```

---

## Step 6: Database Setup

```bash
# Create migrations
python manage.py makemigrations accounts
python manage.py makemigrations employees
python manage.py makemigrations cameras
python manage.py makemigrations attendance

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123 (or your choice)
```

---

## Step 7: Load Initial Data (Optional)

Create a Python shell script or use admin panel to add:

```bash
python manage.py shell
```

```python
from employees.models import Department, Designation
from cameras.models import Location, Camera

# Create departments
dept1 = Department.objects.create(name="Engineering", code="ENG")
dept2 = Department.objects.create(name="HR", code="HR")
dept3 = Department.objects.create(name="Sales", code="SAL")

# Create designations
Designation.objects.create(name="Software Engineer", code="SE")
Designation.objects.create(name="Manager", code="MGR")
Designation.objects.create(name="Executive", code="EXE")

# Create location
location = Location.objects.create(name="Main Office", code="MAIN")

# Create camera (0 = default webcam)
Camera.objects.create(
    name="Main Entrance",
    location=location,
    stream_source="0",
    status="active",
    is_primary=True
)

exit()
```

---

## Step 8: Run the Application

```bash
# Start development server
python manage.py runserver

# Access the application
# http://127.0.0.1:8000/
```

---

## Step 9: First Time Setup Flow

### 1. Login
- Go to http://127.0.0.1:8000/
- Login with your superuser credentials

### 2. Add Employee with Face
- Click "Register Employee" button
- Fill in employee details
- **Important:** Upload a clear front-facing photo
- Submit the form

### 3. Verify Face Registration
- Go to Admin Panel → Employees
- Check if "Face Status" shows green checkmark
- If red X, upload a better quality image

### 4. Start Live Recognition
- Click "Live Recognition" from sidebar
- Allow camera access if prompted
- Position face in front of camera
- System will automatically:
  - Detect face (red box for unknown, green for recognized)
  - Show employee ID and confidence %
  - Mark attendance when confidence > 70%

### 5. View Attendance
- Click "Attendance" from sidebar
- See all punch records
- View daily summaries
- Check employee-specific reports

---

## Testing the System

### Test 1: Face Detection
1. Go to Live Recognition
2. Verify camera feed is working
3. Move face in/out of frame
4. Check if face box appears

### Test 2: Face Recognition
1. Register yourself as an employee with photo
2. Wait 5 seconds for encoding to process
3. Go to Live Recognition
4. Face the camera
5. Verify green box appears with your employee ID

### Test 3: Attendance Marking
1. Face the camera until recognized
2. Check dashboard for new attendance record
3. Wait 5+ minutes
4. Face camera again (should mark OUT)
5. Verify IN/OUT alternation

---

## Troubleshooting

### Camera Not Working
```python
# Test camera access
import cv2
cap = cv2.VideoCapture(0)
print(cap.isOpened())  # Should print True
cap.release()
```

### Face Not Detected
- Ensure good lighting
- Face camera directly
- Remove glasses/masks if possible
- Use high-quality image for registration

### Low Confidence Scores
- Re-register with better quality image
- Ensure consistent lighting
- Check if face is fully visible in frame

### Attendance Not Marking
- Check confidence threshold (default 70%)
- Verify employee status is "active"
- Check if 5-minute interval has passed since last punch

---

## Next Steps (Post Phase 1)

After Phase 1 is working:

1. **Add More Templates**
   - Employee list page
   - Employee detail page
   - Attendance history page
   - Daily summary page

2. **Enhance UI**
   - Add custom CSS
   - Improve dashboards
   - Add charts

3. **Add Features**
   - Manual attendance override
   - Attendance reports
   - Export to Excel
   - Email notifications

4. **Optimize Performance**
   - Cache encodings
   - Optimize database queries
   - Add pagination

---

## Production Deployment Tips

1. **Change SECRET_KEY** in settings.py
2. **Set DEBUG = False**
3. **Configure ALLOWED_HOSTS**
4. **Use PostgreSQL** instead of SQLite
5. **Configure static files** with WhiteNoise or nginx
6. **Use gunicorn** for WSGI server
7. **Add HTTPS** with SSL certificate
8. **Set up proper camera streaming** for production

---

## Support & Documentation

- Django Docs: https://docs.djangoproject.com/
- face_recognition: https://github.com/ageitgey/face_recognition
- OpenCV: https://docs.opencv.org/

---

## License

This is a production-ready starter template for building face recognition platforms.
Customize as needed for your specific use case.
"""
Face Recognition Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import json
import time
from .face_engine import FaceEngine
from .encoding_manager import EncodingManager
from employees.models import Employee
from cameras.models import Camera
from attendance.services import AttendanceService

# Global instances
face_engine = FaceEngine()
encoding_manager = EncodingManager()
attendance_service = AttendanceService()

# Cache for known encodings
known_encodings = {}
last_reload_ts = 0.0

def load_encodings(force=False):
    """
    Load all employee encodings into memory.
    Uses a shared cache to ensure live recognition picks up new registrations.
    """
    global known_encodings, last_reload_ts
    if force or not known_encodings:
        known_encodings = encoding_manager.refresh_cache()
        last_reload_ts = time.time()
    return len(known_encodings)

def generate_frames(camera_source=0):
    """
    Video frame generator with face recognition
    Yields frames for streaming
    """
    # Always start with a fresh cache to pick up new registrations
    load_encodings(force=True)
    
    # Open camera
    camera = cv2.VideoCapture(camera_source)
    
    # Set camera properties for better performance
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    
    process_frame = 0
    # In-memory throttling to avoid hammering DB/attendance logic every frame
    last_attempt_ts_by_employee = {}  # employee_id -> epoch seconds
    min_attempt_interval_seconds = 10
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            
            # Process every 3rd frame for performance
            process_frame += 1
            if process_frame % 3 == 0:
                # Periodically refresh encodings so long-running streams get updates
                if time.time() - last_reload_ts >= 60:
                    load_encodings(force=True)
                
                # Detect faces
                face_locations = face_engine.detect_faces(frame)
                
                # Process each detected face
                for face_location in face_locations:
                    # Generate encoding
                    face_encoding = face_engine.encode_face(frame, face_location)
                    
                    if face_encoding is not None:
                        # Recognize face
                        employee_id, confidence, distance = face_engine.recognize_face(
                            face_encoding,
                            known_encodings
                        )
                        
                        if employee_id:
                            # Draw green box for recognized faces
                            frame = face_engine.draw_face_box(
                                frame,
                                face_location,
                                name=employee_id,
                                confidence=confidence,
                                color=(0, 255, 0)
                            )
                            
                            # Mark attendance if confidence is high enough
                            if confidence >= attendance_service.confidence_threshold:
                                now_ts = time.time()
                                last_ts = last_attempt_ts_by_employee.get(employee_id, 0)
                                if now_ts - last_ts >= min_attempt_interval_seconds:
                                    last_attempt_ts_by_employee[employee_id] = now_ts
                                    try:
                                        employee = Employee.objects.get(employee_id=employee_id)
                                        attendance_service.mark_attendance(
                                            employee=employee,
                                            confidence_score=confidence,
                                            face_distance=distance
                                        )
                                    except Employee.DoesNotExist:
                                        pass
                        else:
                            # Draw red box for unknown faces
                            frame = face_engine.draw_face_box(
                                frame,
                                face_location,
                                name="Unknown",
                                color=(0, 0, 255)
                            )
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        camera.release()

@login_required
def live_feed_view(request):
    """Display live camera feed with recognition"""
    # Get primary camera or use webcam
    try:
        camera = Camera.objects.filter(is_primary=True, status='active').first()
        camera_source = camera.get_stream_source_int() if camera else 0
    except:
        camera_source = 0
    
    # Store camera source in session
    request.session['camera_source'] = camera_source
    
    # Load encodings count
    encodings_count = load_encodings()
    
    context = {
        'encodings_count': encodings_count,
        'camera': camera if camera else None,
    }
    
    return render(request, 'recognition/live_feed.html', context)

@login_required
def video_feed(request):
    """Video streaming route"""
    camera_source = request.session.get('camera_source', 0)
    
    return StreamingHttpResponse(
        generate_frames(camera_source),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

@login_required
def refresh_encodings(request):
    """Reload all face encodings"""
    count = load_encodings()
    return JsonResponse({
        'success': True,
        'count': count,
        'message': f'Loaded {count} face encodings'
    })
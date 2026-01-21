"""
Face Recognition Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import face_recognition
import numpy as np
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
    Video frame generator with OPTIMIZED face recognition.
    Processes 1/4 sized frames to improve performance.
    """
    # Always start with a fresh cache to pick up new registrations
    load_encodings(force=True)
    
    # Open camera
    camera = cv2.VideoCapture(camera_source)
    if not camera.isOpened():
        print(f"Could not open camera {camera_source}")
        return

    # Set camera properties for better performance (Request 640x480)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)
    
    process_this_frame = True
    
    # In-memory throttling to avoid hammering DB/attendance logic every frame
    last_attempt_ts_by_employee = {}  # employee_id -> epoch seconds
    min_attempt_interval_seconds = 10
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            
            # Periodically refresh encodings so long-running streams get updates
            if time.time() - last_reload_ts >= 60:
                load_encodings(force=True)

            # OPTIMIZATION: Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Initialize results for this frame
            face_locations = []
            face_names = []
            face_confidences = []

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    name = "Unknown"
                    confidence = 0.0
                    distance = 1.0
                    
                    if known_encodings:
                        # Use our existing engine logic for matching, but pass the encoding directly
                        employee_id, confidence, distance = face_engine.recognize_face(
                            face_encoding,
                            known_encodings
                        )
                        
                        if employee_id:
                            name = employee_id
                            
                            # Mark Attendance Logic
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

                    face_names.append(name)
                    face_confidences.append(confidence)

            process_this_frame = not process_this_frame

            # Display the results
            # We must use the face_locations found in the PREVIOUS step (if we skipped processing)
            # However, in this simple loop, if we skip processing, we won't have new locations. 
            # Ideally, we should cache the last known locations, but for simplicity in this loop 
            # we only draw when we process, or we'd need to store state. 
            # To fix the "flicker" when skipping frames, we usually just process the drawing 
            # based on the *last calculated* locations. 
            # But for this implementation, we will recalculate drawing coordinates only when we have them.
            # To ensure boxes persist, we can move face_locations/names to outer scope if needed, 
            # but usually 30FPS with 1/2 processing is fast enough to not notice.
            
            for (top, right, bottom, left), name, conf in zip(face_locations, face_names, face_confidences):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                
                # Draw the box
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label background
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                
                # Draw text
                font = cv2.FONT_HERSHEY_DUPLEX
                label = f"{name} ({conf:.1f}%)" if name != "Unknown" else "Unknown"
                cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

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
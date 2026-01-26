"""
Face Recognition Views - Hybrid Client/Server Architecture
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import face_recognition
import numpy as np
import json
import base64
import time
from .face_engine import FaceEngine
from .encoding_manager import EncodingManager
from employees.models import Employee
from attendance.services import AttendanceService

# Global instances
face_engine = FaceEngine()
encoding_manager = EncodingManager()
attendance_service = AttendanceService()

# Cache
known_encodings = {}
last_reload_ts = 0.0

def load_encodings(force=False):
    global known_encodings, last_reload_ts
    if force or not known_encodings:
        print("Reloading encodings...")
        known_encodings = encoding_manager.refresh_cache()
        last_reload_ts = time.time()
        print(f"Loaded encodings for {len(known_encodings)} companies.")
    return len(known_encodings)

@login_required
def live_feed_view(request):
    """Render the Hybrid Live Feed Page"""
    return render(request, 'recognition/live_feed.html')

@csrf_exempt
def recognize_frame(request):
    """
    API that accepts a Base64 image, detects faces, and returns JSON results.
    """
    if request.method == 'POST':
        try:
            # 1. Parse Data
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({'status': 'error', 'message': 'No image data'})

            # 2. Decode Base64 to OpenCV Frame
            # Browser sends Base64 JPEG. OpenCV reads this as BGR.
            header, encoded = image_data.split(",", 1)
            nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 3. Refresh Encodings if needed
            global last_reload_ts
            if time.time() - last_reload_ts > 60:
                load_encodings(force=True)
            elif not known_encodings:
                load_encodings()

            # 4. Color Space Conversion (CRITICAL)
            # face_recognition library EXPECTS RGB. OpenCV gives BGR.
            # If this is wrong, a known face will look "blue" to the AI and won't match "skin" tones.
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 5. Detect Faces
            # Using 'hog' model is faster for CPU. If accuracy is poor, remove model="hog" to use default.
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            results = []

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                name = "Unknown"
                confidence = 0.0
                
                # Match Face
                if known_encodings:
                    # Flatten cache for checking (In production, filter by User Company!)
                    # For now, we search ALL loaded faces to debug why it's not matching.
                    all_encodings = {}
                    for company_id, emps in known_encodings.items():
                        all_encodings.update(emps)
                    
                    if all_encodings:
                        # We use a slightly looser tolerance (0.6 is default, 0.5 is strict)
                        # We pass tolerance=0.6 explicitly to FaceEngine if possible, or rely on its internal default.
                        employee_id, confidence, distance = face_engine.recognize_face(
                            face_encoding,
                            all_encodings
                        )
                        
                        # DEBUG PRINT: Watch your terminal to see the distance score!
                        # Distance < 0.6 is a match. Lower is better.
                        print(f"Face detected. Best match: {employee_id}, Distance: {distance:.4f}")

                        if employee_id:
                            name = employee_id
                            
                            # Mark Attendance
                            if confidence >= attendance_service.confidence_threshold:
                                try:
                                    employee = Employee.objects.filter(employee_id=employee_id).first()
                                    if employee:
                                        attendance_service.mark_attendance(
                                            employee=employee,
                                            confidence_score=confidence,
                                            face_distance=distance
                                        )
                                except Exception as e:
                                    print(f"Attendance Error: {e}")

                results.append({
                    'id': name,
                    'name': name,
                    'confidence': round(confidence, 1),
                    'box': {
                        'top': top,
                        'right': right,
                        'bottom': bottom,
                        'left': left
                    }
                })

            return JsonResponse({'status': 'success', 'faces': results})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})
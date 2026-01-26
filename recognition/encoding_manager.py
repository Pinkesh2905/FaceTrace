"""
Face Encoding Manager
Handles loading, caching, and managing employee face encodings
"""
import numpy as np
from pathlib import Path
from django.conf import settings
from employees.models import Employee
from .face_engine import FaceEngine

class EncodingManager:
    """
    Manages face encodings for all employees
    """
    
    def __init__(self):
        self.face_engine = FaceEngine()
        self.encodings_cache = {}
        self.encodings_dir = settings.FACE_ENCODINGS_DIR
        self._ensure_directories()
    
    def _ensure_directories(self):
        Path(self.encodings_dir).mkdir(parents=True, exist_ok=True)
        Path(settings.FACE_IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    
    def get_encoding_path(self, employee):
        """Get file path for employee's encoding"""
        return Path(settings.MEDIA_ROOT) / employee.get_encoding_filename()
    
    def save_employee_encoding(self, employee, image_path):
        """Generate and save face encoding."""
        try:
            print(f"DEBUG: Generatng encoding for {employee.employee_id} from {image_path}")
            encoding, face_count = self.face_engine.encode_face_from_file(image_path)
            
            if face_count == 0: 
                print("DEBUG: No face found in image")
                return False, "No face detected."
            
            if face_count > 1: 
                print("DEBUG: Multiple faces found")
                return False, "Multiple faces detected."
            
            if encoding is None: 
                print("DEBUG: Encoding failed")
                return False, "Unable to encode face."
            
            encoding_path = self.get_encoding_path(employee)
            print(f"DEBUG: Saving encoding to {encoding_path}")
            self.face_engine.save_encoding(encoding, encoding_path)
            
            employee.face_encoding_path = str(encoding_path)
            employee.is_face_registered = True
            employee.save()
            
            return True, None
        except Exception as e:
            print(f"ERROR: {e}")
            return False, str(e)
    
    def load_all_encodings(self):
        """
        Load ALL encodings.
        """
        print("DEBUG: Starting load_all_encodings...")
        employees = Employee.objects.filter(is_face_registered=True, status='active')
        print(f"DEBUG: Found {employees.count()} active employees with is_face_registered=True")
        
        # Structure: { company_id: { employee_id: encoding } }
        cache = {}
        
        for employee in employees:
            # DEBUG: Check company link
            company_id = employee.company_id if employee.company_id else "NO_COMPANY"
            
            # Initialize company dict if missing
            if company_id not in cache:
                cache[company_id] = {}
                
            path = self.get_encoding_path(employee)
            
            if not path.exists():
                print(f"DEBUG: Encoding file missing for {employee.employee_id} at {path}")
                continue
                
            encoding = self.face_engine.load_encoding(path)
            
            if encoding is not None:
                cache[company_id][employee.employee_id] = encoding
                print(f"DEBUG: Loaded encoding for {employee.employee_id} (Company: {company_id})")
            else:
                print(f"DEBUG: Failed to load pickle for {employee.employee_id}")
                
        return cache
    
    def refresh_cache(self, company_id=None):
        self.encodings_cache = self.load_all_encodings()
        return self.encodings_cache
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
    Provides efficient loading and caching
    """
    
    def __init__(self):
        self.face_engine = FaceEngine()
        self.encodings_cache = {}
        self.encodings_dir = settings.FACE_ENCODINGS_DIR
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create required directories if they don't exist"""
        Path(self.encodings_dir).mkdir(parents=True, exist_ok=True)
        Path(settings.FACE_IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    
    def get_encoding_path(self, employee_id):
        """Get file path for employee's encoding"""
        return Path(self.encodings_dir) / f"{employee_id}.npy"
    
    def save_employee_encoding(self, employee, image_path):
        """
        Generate and save face encoding for an employee.
        
        Returns:
            (success: bool, error_message: str | None)
        """
        try:
            encoding, face_count = self.face_engine.encode_face_from_file(image_path)
            
            if face_count == 0:
                return False, "No face detected in the uploaded image. Please upload a clear, front-facing photo."
            
            if face_count > 1:
                return False, "Multiple faces detected in the uploaded image. Please upload a photo with only the employee's face."
            
            if encoding is None:
                return False, "Unable to process the face encoding. Try a clearer image."
            
            # Save encoding to file
            encoding_path = self.get_encoding_path(employee.employee_id)
            self.face_engine.save_encoding(encoding, encoding_path)
            
            # Update employee record
            employee.face_encoding_path = str(encoding_path)
            employee.is_face_registered = True
            employee.save()
            
            # Update cache
            self.encodings_cache[employee.employee_id] = encoding
            
            return True, None
            
        except Exception as e:
            error_msg = f"Error saving encoding for {employee.employee_id}: {e}"
            print(error_msg)
            return False, error_msg
    
    def load_employee_encoding(self, employee_id):
        """
        Load encoding for a single employee
        
        Returns:
            numpy array or None
        """
        # Check cache first
        if employee_id in self.encodings_cache:
            return self.encodings_cache[employee_id]
        
        # Load from file
        encoding_path = self.get_encoding_path(employee_id)
        encoding = self.face_engine.load_encoding(encoding_path)
        
        if encoding is not None:
            self.encodings_cache[employee_id] = encoding
        
        return encoding
    
    def load_all_encodings(self):
        """
        Load all employee encodings into memory
        
        Returns:
            dict {employee_id: encoding}
        """
        employees = Employee.objects.filter(
            is_face_registered=True,
            status='active'
        )
        
        encodings_dict = {}
        
        for employee in employees:
            encoding = self.load_employee_encoding(employee.employee_id)
            if encoding is not None:
                encodings_dict[employee.employee_id] = encoding
        
        return encodings_dict
    
    def delete_employee_encoding(self, employee_id):
        """
        Delete encoding for an employee
        """
        encoding_path = self.get_encoding_path(employee_id)
        
        # Delete file
        if encoding_path.exists():
            encoding_path.unlink()
        
        # Remove from cache
        if employee_id in self.encodings_cache:
            del self.encodings_cache[employee_id]
    
    def refresh_cache(self):
        """
        Refresh the encodings cache
        """
        self.encodings_cache = {}
        return self.load_all_encodings()
    
    def get_cache_size(self):
        """
        Get number of encodings in cache
        """
        return len(self.encodings_cache)
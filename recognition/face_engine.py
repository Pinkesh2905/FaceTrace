"""
Core Face Recognition Engine using face_recognition library
"""
import cv2
import face_recognition
import numpy as np
from pathlib import Path
from django.conf import settings

class FaceEngine:
    """
    Core face recognition engine
    Handles face detection, encoding, and recognition
    """
    
    def __init__(self):
        self.tolerance = 0.6  # Lower = stricter matching
        self.model = 'hog'  # 'hog' is faster, 'cnn' is more accurate but needs GPU
        
    def detect_faces(self, image):
        """
        Detect faces in an image
        Returns list of face locations
        """
        # Convert BGR (OpenCV) to RGB (face_recognition)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find all face locations
        face_locations = face_recognition.face_locations(rgb_image, model=self.model)
        
        return face_locations
    
    def encode_face(self, image, face_location=None):
        """
        Generate face encoding from image
        Returns 128-dimensional face encoding vector
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if face_location is not None:
            # Use provided face location
            encodings = face_recognition.face_encodings(rgb_image, [face_location])
        else:
            # Auto-detect face
            encodings = face_recognition.face_encodings(rgb_image)
        
        if encodings:
            return encodings[0]
        return None
    
    def encode_face_from_file(self, image_path):
        """
        Load image from file and generate encoding.
        Returns (encoding, face_count) to allow callers to validate quality.
        """
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if encodings:
            return encodings[0], len(encodings)
        return None, 0
    
    def compare_faces(self, known_encoding, face_encoding):
        """
        Compare a face encoding against a known encoding
        Returns (match, distance)
        """
        if known_encoding is None or face_encoding is None:
            return False, 1.0
        
        # Calculate face distance
        distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
        
        # Check if match
        matches = face_recognition.compare_faces(
            [known_encoding], 
            face_encoding, 
            tolerance=self.tolerance
        )
        
        return matches[0], float(distance)
    
    def recognize_face(self, face_encoding, known_encodings_dict):
        """
        Recognize face against database of known encodings
        
        Args:
            face_encoding: encoding to match
            known_encodings_dict: {employee_id: encoding}
        
        Returns:
            (employee_id, confidence, distance) or (None, 0, 1.0)
        """
        # NOTE: numpy arrays cannot be used in boolean context ("if face_encoding")
        if face_encoding is None or not known_encodings_dict:
            return None, 0, 1.0
        
        best_match = None
        best_distance = 1.0
        
        for employee_id, known_encoding in known_encodings_dict.items():
            is_match, distance = self.compare_faces(known_encoding, face_encoding)
            
            if is_match and distance < best_distance:
                best_distance = distance
                best_match = employee_id
        
        if best_match:
            # Calculate confidence percentage (inverse of distance)
            confidence = max(0, min(100, (1 - best_distance) * 100))
            return best_match, confidence, best_distance
        
        return None, 0, 1.0
    
    def draw_face_box(self, frame, face_location, name=None, confidence=None, color=(0, 255, 0)):
        """
        Draw bounding box around detected face
        """
        top, right, bottom, left = face_location
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label background
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        
        # Draw text
        font = cv2.FONT_HERSHEY_DUPLEX
        if name and confidence:
            text = f"{name} ({confidence:.1f}%)"
        elif name:
            text = name
        else:
            text = "Unknown"
        
        cv2.putText(frame, text, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def save_encoding(self, encoding, filepath):
        """
        Save face encoding to file
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        np.save(filepath, encoding)
    
    def load_encoding(self, filepath):
        """
        Load face encoding from file
        """
        if Path(filepath).exists():
            return np.load(filepath)
        return None
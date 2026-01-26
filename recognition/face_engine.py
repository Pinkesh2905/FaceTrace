import face_recognition
import numpy as np
import cv2
import pickle
from pathlib import Path

class FaceEngine:
    """
    Core face recognition logic wrapper.
    Ensures consistent RGB processing for both registration and recognition.
    """
    
    def encode_face_from_file(self, file_path):
        """
        Generates encoding from an image file (Registration).
        Returns (encoding, face_count)
        """
        try:
            # load_image_file loads image in RGB format automatically
            image = face_recognition.load_image_file(file_path)
            
            # Detect faces
            # We use the default model here as accuracy > speed for registration
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return None, 0
                
            encodings = face_recognition.face_encodings(image, face_locations)
            
            # Return the first found face encoding and the total count
            return encodings[0], len(face_locations)
        except Exception as e:
            print(f"Error encoding file {file_path}: {e}")
            return None, 0

    def recognize_face(self, unknown_encoding, known_encodings_dict, tolerance=0.6):
        """
        Compares an encoding against a dictionary of {id: encoding}.
        
        Args:
            unknown_encoding: The 128D vector from the live camera.
            known_encodings_dict: Dictionary {employee_id: known_encoding}.
            tolerance: Distance threshold. 
                       0.6 is default. 
                       0.5 is strict. 
                       0.55 is a good balance for webcam.
        
        Returns:
            (best_match_id, confidence_percent, min_distance)
        """
        if unknown_encoding is None or not known_encodings_dict:
            return None, 0.0, 1.0
            
        known_ids = list(known_encodings_dict.keys())
        known_encodings_list = list(known_encodings_dict.values())
        
        # Calculate Euclidean distance to all known faces
        # Lower distance = Better match
        distances = face_recognition.face_distance(known_encodings_list, unknown_encoding)
        
        # Find the best match index
        best_match_index = np.argmin(distances)
        min_distance = distances[best_match_index]
        
        # DEBUG: Print the closest match distance to console
        # This helps debug why a face might be "Unknown"
        best_match_id_debug = known_ids[best_match_index]
        print(f"DEBUG: Best match: {best_match_id_debug}, Distance: {min_distance:.4f}, Threshold: {tolerance}")

        # Check if the best match is within tolerance
        if min_distance <= tolerance:
            best_match_id = known_ids[best_match_index]
            
            # Calculate a user-friendly "confidence" score (0-100%)
            # This is not a probability, but a normalized distance score.
            # 0.0 dist -> 100% conf
            # tolerance dist -> 0% conf
            if min_distance > tolerance:
                confidence = 0.0
            else:
                confidence = max(0, (1.0 - (min_distance / tolerance)) * 100)
            
            return best_match_id, confidence, min_distance
            
        return None, 0.0, min_distance

    def save_encoding(self, encoding, path):
        """Save encoding to a binary pickle file"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'wb') as f:
                pickle.dump(encoding, f)
        except Exception as e:
            print(f"Error saving encoding to {path}: {e}")

    def load_encoding(self, path):
        """Load encoding from a binary pickle file"""
        try:
            if not Path(path).exists():
                return None
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading encoding from {path}: {e}")
            return None
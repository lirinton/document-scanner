"""
Camera and image processing module for document scanner.
Handles USB camera access, image capture, and preprocessing.
"""

import cv2
import numpy as np
import os
import tempfile
from datetime import datetime

def check_camera_available(camera_index=0):
    """Check if camera is available and accessible."""
    cap = None
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return False
        
        # Try to read a frame
        ret, frame = cap.read()
        return ret and frame is not None
        
    except Exception as e:
        print(f"Camera check error: {e}")
        return False
    finally:
        if cap is not None:
            cap.release()

def capture_and_process_image(camera_index=0, resolution=(1920, 1080), timeout=30):
    """
    Capture image from USB camera and preprocess for OCR.
    
    Returns:
        tuple: (image_path, error_message)
    """
    cap = None
    try:
        print(f"Initializing camera {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            return None, f"Could not open camera {camera_index}"
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        
        print("Camera opened, adjusting settings...")
        
        # Allow camera to adjust to lighting (capture a few frames)
        for i in range(5):
            ret, frame = cap.read()
            if not ret:
                return None, "Failed to capture initial frames"
            time.sleep(0.1)  # Small delay between frames
        
        # Capture final frame for processing
        ret, frame = cap.read()
        if not ret or frame is None:
            return None, "Failed to capture image frame"
        
        print(f"Image captured: {frame.shape}")
        
        # Process image for OCR
        processed_image = preprocess_image(frame)
        
        # Save to temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        image_path = os.path.join(temp_dir, f"document_scan_{timestamp}.jpg")
        
        success = cv2.imwrite(image_path, processed_image)
        if not success:
            return None, "Failed to save processed image"
        
        print(f"Image saved to: {image_path}")
        return image_path, None
        
    except Exception as e:
        return None, f"Capture error: {str(e)}"
    finally:
        if cap is not None:
            cap.release()
            print("Camera released")

def preprocess_image(image):
    """
    Preprocess image for better OCR results.
    Applies grayscale conversion, noise reduction, contrast enhancement, and thresholding.
    """
    try:
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Noise reduction
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Contrast enhancement using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Thresholding to create binary image
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
        
    except Exception as e:
        print(f"Image processing error: {e}, returning original image")
        return image

# Test the camera if run directly
if __name__ == "__main__":
    print("Testing camera...")
    available = check_camera_available()
    print(f"Camera available: {available}")
    
    if available:
        image_path, error = capture_and_process_image()
        if error:
            print(f"Capture test failed: {error}")
        else:
            print(f"Capture test successful: {image_path}")
"""
OCR processing module using Tesseract.
Handles text extraction from images.
"""

import pytesseract
from PIL import Image
import os

def ocr_image(image_path, lang='eng', config=''):
    """
    Perform OCR on image file.
    
    Returns:
        tuple: (extracted_text, error_message)
    """
    try:
        if not os.path.exists(image_path):
            return None, "Image file not found"
        
        print(f"Performing OCR on: {image_path}")
        
        # Open and validate image
        try:
            with Image.open(image_path) as img:
                # Verify it's a valid image and convert if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Use pytesseract to extract text
                custom_config = config if config else '--psm 6'
                text = pytesseract.image_to_string(img, lang=lang, config=custom_config)
                
                # Clean up text
                cleaned_text = text.strip()
                
                print(f"OCR completed, extracted {len(cleaned_text)} characters")
                return cleaned_text, None
                
        except Exception as e:
            return None, f"Image processing error: {str(e)}"
            
    except pytesseract.TesseractNotFoundError:
        return None, "Tesseract OCR not installed. Please run: sudo apt install tesseract-ocr"
    except Exception as e:
        return None, f"OCR processing error: {str(e)}"

# Test function
if __name__ == "__main__":
    # Test OCR with a sample message
    test_text, error = ocr_image("/nonexistent/test.jpg")
    if error:
        print(f"OCR test completed (expected error): {error}")
    else:
        print(f"OCR test result: {test_text}")
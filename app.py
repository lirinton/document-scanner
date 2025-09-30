"""
Flask web application for web-based document scanner.
Serves web interface at http://localhost:5000
API endpoints for scanning and OCR
Real-time camera status and scanning feedback
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import threading
import time
import os
import scanner
import ocr_processor

# Configuration
CAMERA_INDEX = 0
CAMERA_RESOLUTION = (1920, 1080)
SCAN_TIMEOUT = 30
OCR_LANGUAGE = 'eng'
OCR_CONFIG = '--psm 6'
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

app = Flask(__name__, static_folder='static', template_folder='templates')

# In-memory storage for last scan result
last_scan_result = {
    "text": "",
    "timestamp": None,
    "success": False,
    "error": None
}
scan_in_progress = False
scan_lock = threading.Lock()

def get_camera_status():
    """Check camera status and availability"""
    try:
        available = scanner.check_camera_available(CAMERA_INDEX)
        return {
            "camera_online": available,
            "resolution": CAMERA_RESOLUTION if available else None,
            "status": "online" if available else "offline"
        }
    except Exception as e:
        return {
            "camera_online": False,
            "resolution": None,
            "status": "error",
            "error": str(e)
        }

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('index.html')

@app.route('/status')
def status():
    """Return system and camera status"""
    status = get_camera_status()
    status['scan_in_progress'] = scan_in_progress
    return jsonify(status)

@app.route('/scan', methods=['POST'])
def scan_document():
    """Trigger document scan and OCR processing"""
    global scan_in_progress, last_scan_result
    
    with scan_lock:
        if scan_in_progress:
            return jsonify({"success": False, "error": "Scan already in progress"}), 429
        
        scan_in_progress = True

    def perform_scan():
        global scan_in_progress, last_scan_result
        try:
            print("Starting document scan...")
            
            # Step 1: Capture and process image
            image_path, capture_error = scanner.capture_and_process_image(
                camera_index=CAMERA_INDEX,
                resolution=CAMERA_RESOLUTION,
                timeout=SCAN_TIMEOUT
            )
            
            if capture_error:
                last_scan_result = {
                    "text": "",
                    "timestamp": time.time(),
                    "success": False,
                    "error": f"Capture failed: {capture_error}"
                }
                return

            # Step 2: Perform OCR
            text, ocr_error = ocr_processor.ocr_image(
                image_path=image_path,
                lang=OCR_LANGUAGE,
                config=OCR_CONFIG
            )
            
            # Clean up the temporary image file
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except:
                pass

            if ocr_error:
                last_scan_result = {
                    "text": "",
                    "timestamp": time.time(),
                    "success": False,
                    "error": f"OCR failed: {ocr_error}"
                }
            else:
                last_scan_result = {
                    "text": text or "No text detected",
                    "timestamp": time.time(),
                    "success": True,
                    "error": None
                }
                print("Scan completed successfully")
                
        except Exception as e:
            last_scan_result = {
                "text": "",
                "timestamp": time.time(),
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
        finally:
            scan_in_progress = False

    # Start scan in background thread
    scan_thread = threading.Thread(target=perform_scan, daemon=True)
    scan_thread.start()
    
    return jsonify({"success": True, "message": "Scan started successfully"})

@app.route('/last_result')
def get_last_result():
    """Get the result of the last scan"""
    return jsonify(last_scan_result)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

if __name__ == '__main__':
    print(f"Starting Document Scanner on http://{HOST}:{PORT}")
    print("Make sure the USB camera is connected and accessible")
    app.run(host=HOST, port=PORT, debug=DEBUG)
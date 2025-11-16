"""
MAIN APPLICATION - Number Plate Recognition System
Entry point with configuration integration
"""

import cv2
import pytesseract
import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime
from collections import deque
import time
import re
import sys

# Import configuration
try:
    import config
except ImportError:
    print("ERROR: config.py not found!")
    print("Please ensure config.py is in the same directory")
    sys.exit(1)

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

# ==================== DATABASE INITIALIZATION ====================
def init_database():
    """Initialize SQLite database"""
    try:
        config.create_directories()
        
        conn = sqlite3.connect(config.DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                plate_number TEXT NOT NULL,
                confidence REAL,
                image_path TEXT,
                location TEXT,
                processing_time REAL,
                detection_method TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                total_detections INTEGER,
                unique_plates INTEGER,
                avg_confidence REAL,
                avg_processing_time REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# ==================== PREPROCESSING ====================
class PlatePreprocessor:
    """Image preprocessing for OCR"""
    
    @staticmethod
    def adaptive_threshold(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        return thresh
    
    @staticmethod
    def otsu_threshold(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    @staticmethod
    def clahe_enhance(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

# ==================== OCR ENGINE ====================
class SmartOCR:
    """Advanced OCR with multiple methods"""
    
    def __init__(self):
        self.preprocessor = PlatePreprocessor()
    
    def extract_text(self, plate_img):
        """Extract text using multiple methods"""
        methods = [
            ('Adaptive', self.preprocessor.adaptive_threshold),
            ('Otsu', self.preprocessor.otsu_threshold),
            ('CLAHE', self.preprocessor.clahe_enhance)
        ]
        
        results = []
        
        for method_name, method_func in methods:
            try:
                processed = method_func(plate_img)
                
                for psm_config in [config.OCR_CONFIG_PSM7, config.OCR_CONFIG_PSM8]:
                    data = pytesseract.image_to_data(processed, config=psm_config,
                                                     output_type=pytesseract.Output.DICT)
                    
                    text = ""
                    confidences = []
                    
                    for i, word in enumerate(data['text']):
                        if int(data['conf'][i]) > 0:
                            text += word
                            confidences.append(int(data['conf'][i]))
                    
                    text = text.strip().replace(" ", "").upper()
                    
                    if text and len(text) >= config.MIN_PLATE_LENGTH:
                        avg_conf = sum(confidences) / len(confidences) if confidences else 0
                        results.append((text, avg_conf / 100, method_name))
            
            except Exception:
                continue
        
        if not results:
            return "", 0, "None"
        
        return max(results, key=lambda x: x[1])
    
    def validate_plate(self, text):
        """Validate plate format"""
        if len(text) < config.MIN_PLATE_LENGTH or len(text) > config.MAX_PLATE_LENGTH:
            return False
        return bool(re.match(r'^[A-Z0-9]+$', text))

# ==================== DUPLICATE MANAGER ====================
class DuplicateManager:
    """Prevent duplicate detections"""
    
    def __init__(self):
        self.detected = deque()
    
    def is_duplicate(self, plate_text):
        """Check if plate detected recently"""
        current_time = time.time()
        
        # Remove old entries
        while self.detected and current_time - self.detected[0][1] > config.DUPLICATE_TIME_WINDOW:
            self.detected.popleft()
        
        # Check duplicates
        for plate, _ in self.detected:
            if plate == plate_text:
                return True
        
        self.detected.append((plate_text, current_time))
        return False

# ==================== PERFORMANCE MONITOR ====================
class PerformanceMonitor:
    """Track performance metrics"""
    
    def __init__(self):
        self.frame_times = deque(maxlen=config.PERFORMANCE_BUFFER_SIZE)
    
    def add_frame_time(self, duration):
        self.frame_times.append(duration)
    
    def get_fps(self):
        if not self.frame_times:
            return 0
        return 1.0 / (sum(self.frame_times) / len(self.frame_times))

# ==================== DATA MANAGER ====================
class DataManager:
    """Handle data storage"""
    
    def save_detection(self, plate_data):
        """Save to database and CSV"""
        try:
            # Database
            conn = sqlite3.connect(config.DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO plates (timestamp, plate_number, confidence, image_path,
                                  location, processing_time, detection_method)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', plate_data)
            conn.commit()
            conn.close()
            
            # CSV backup
            df = pd.DataFrame([{
                'Timestamp': plate_data[0],
                'Plate_Number': plate_data[1],
                'Confidence': f"{plate_data[2]:.2%}",
                'Image_Path': plate_data[3]
            }])
            
            if os.path.exists(config.CSV_FILE):
                df.to_csv(config.CSV_FILE, mode='a', header=False, index=False)
            else:
                df.to_csv(config.CSV_FILE, index=False)
            
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def get_statistics(self):
        """Get today's statistics"""
        try:
            conn = sqlite3.connect(config.DATABASE_FILE)
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('SELECT COUNT(*) FROM plates WHERE DATE(timestamp) = ?', (today,))
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT plate_number) FROM plates WHERE DATE(timestamp) = ?', (today,))
            unique = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(confidence) FROM plates WHERE DATE(timestamp) = ?', (today,))
            avg_conf = cursor.fetchone()[0] or 0
            
            conn.close()
            return total, unique, avg_conf
        except:
            return 0, 0, 0

# ==================== UI FUNCTIONS ====================
def draw_dashboard(frame, stats, perf_monitor, mode, auto_save):
    """Draw statistics dashboard"""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (410, 190), config.COLOR_DASHBOARD_BG, -1)
    frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
    
    fps = perf_monitor.get_fps()
    total, unique, avg_conf = stats
    
    info = [
        ("PLATE RECOGNITION", (255, 255, 0), 0.8),
        (f"FPS: {fps:.1f}", config.COLOR_TEXT, 0.6),
        (f"Mode: {'AUTO' if auto_save else 'MANUAL'}", config.COLOR_TEXT, 0.6),
        (f"Today: {total} detections", config.COLOR_TEXT, 0.6),
        (f"Unique: {unique} plates", config.COLOR_TEXT, 0.6),
        (f"Avg Conf: {avg_conf*100:.1f}%", config.COLOR_TEXT, 0.6)
    ]
    
    y = 40
    for text, color, size in info:
        cv2.putText(frame, text, (20, y), config.TEXT_FONT, size, color, 2)
        y += 28 if size > 0.7 else 25
    
    return frame

def draw_detection_box(frame, x, y, w, h, text, confidence):
    """Draw detection box with info"""
    color = config.COLOR_HIGH_CONFIDENCE if confidence >= config.CONFIDENCE_THRESHOLD else config.COLOR_LOW_CONFIDENCE
    
    cv2.rectangle(frame, (x, y), (x+w, y+h), color, config.BOX_THICKNESS)
    
    # Info box
    cv2.rectangle(frame, (x, y-70), (x+w, y), (0, 0, 0), -1)
    cv2.rectangle(frame, (x, y-70), (x+w, y), color, 2)
    
    cv2.putText(frame, text, (x+5, y-45), config.TEXT_FONT, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"{confidence*100:.1f}%", (x+5, y-20), config.TEXT_FONT, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Press 'S' to save", (x+5, y-5), config.TEXT_FONT, 0.4, (255, 255, 0), 1)

# ==================== MAIN APPLICATION ====================
def main():
    """Main application loop"""
    print("="*70)
    print("  NUMBER PLATE RECOGNITION SYSTEM")
    print("="*70)
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix config.py and try again")
        return
    
    print("\n✓ Configuration validated")
    
    # Initialize
    config.create_directories()
    if not init_database():
        print("❌ Database initialization failed")
        return
    
    print("✓ Database initialized")
    
    # Load cascade
    plate_cascade = cv2.CascadeClassifier(config.CASCADE_PATH)
    if plate_cascade.empty():
        print(f"❌ Cannot load cascade from: {config.CASCADE_PATH}")
        return
    
    print("✓ Cascade loaded")
    
    # Initialize components
    ocr_engine = SmartOCR()
    duplicate_mgr = DuplicateManager()
    data_mgr = DataManager()
    perf_monitor = PerformanceMonitor()
    
    # Open camera
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
    
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("✓ Camera initialized")
    print("\n" + "="*70)
    print("CONTROLS:")
    print("  [A] Toggle Auto-save")
    print("  [S/SPACE] Manual save")
    print("  [D] Toggle Dashboard")
    print("  [Q] Quit")
    print("="*70 + "\n")
    
    # Application state
    auto_save = config.ENABLE_AUTO_SAVE
    show_dashboard = config.ENABLE_DASHBOARD
    frame_count = 0
    
    while True:
        frame_start = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        display_frame = frame.copy()
        
        # Frame skipping
        if frame_count % config.FRAME_SKIP != 0:
            cv2.imshow('Plate Recognition', display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        
        # Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        plates = plate_cascade.detectMultiScale(
            gray,
            scaleFactor=config.CASCADE_SCALE_FACTOR,
            minNeighbors=config.CASCADE_MIN_NEIGHBORS,
            minSize=(config.MIN_PLATE_WIDTH, config.MIN_PLATE_HEIGHT)
        )
        
        # Process plates
        for (x, y, w, h) in plates:
            area = w * h
            if area < config.MIN_PLATE_AREA or area > config.MAX_PLATE_AREA:
                continue
            
            plate_img = frame[y:y+h, x:x+w]
            plate_text, confidence, method = ocr_engine.extract_text(plate_img)
            
            if not ocr_engine.validate_plate(plate_text):
                continue
            
            # Draw detection
            draw_detection_box(display_frame, x, y, w, h, plate_text, confidence)
            
            # Auto-save
            if auto_save and confidence >= config.AUTO_SAVE_THRESHOLD:
                if not duplicate_mgr.is_duplicate(plate_text):
                    timestamp = datetime.now()
                    img_name = f"plate_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                    img_path = os.path.join(config.SAVED_PLATES_DIR, img_name)
                    cv2.imwrite(img_path, plate_img)
                    
                    plate_data = (
                        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        plate_text,
                        confidence,
                        img_path,
                        'Auto',
                        0,
                        method
                    )
                    data_mgr.save_detection(plate_data)
                    print(f"✓ Auto-saved: {plate_text} ({confidence*100:.1f}%)")
        
        # Dashboard
        if show_dashboard:
            stats = data_mgr.get_statistics()
            display_frame = draw_dashboard(display_frame, stats, perf_monitor, "AUTO" if auto_save else "MANUAL", auto_save)
        
        # Display
        cv2.imshow('Plate Recognition - Press Q to Quit', display_frame)
        
        # Performance
        frame_time = time.time() - frame_start
        perf_monitor.add_frame_time(frame_time)
        
        # Controls
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('a'):
            auto_save = not auto_save
            print(f"✓ Auto-save: {'ON' if auto_save else 'OFF'}")
        elif key == ord('d'):
            show_dashboard = not show_dashboard
        elif key in [ord('s'), 32] and len(plates) > 0:
            (x, y, w, h) = plates[0]
            plate_img = frame[y:y+h, x:x+w]
            plate_text, confidence, method = ocr_engine.extract_text(plate_img)
            
            if plate_text and not duplicate_mgr.is_duplicate(plate_text):
                timestamp = datetime.now()
                img_name = f"plate_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                img_path = os.path.join(config.SAVED_PLATES_DIR, img_name)
                cv2.imwrite(img_path, plate_img)
                
                plate_data = (
                    timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    plate_text,
                    confidence,
                    img_path,
                    'Manual',
                    0,
                    method
                )
                data_mgr.save_detection(plate_data)
                print(f"✓ Saved: {plate_text} ({confidence*100:.1f}%)")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Summary
    total, unique, avg_conf = data_mgr.get_statistics()
    print("\n" + "="*70)
    print("  SESSION SUMMARY")
    print("="*70)
    print(f"Total detections: {total}")
    print(f"Unique plates: {unique}")
    print(f"Average confidence: {avg_conf*100:.1f}%")
    print(f"Average FPS: {perf_monitor.get_fps():.1f}")
    print(f"\nData saved in:")
    print(f"  Database: {config.DATABASE_FILE}")
    print(f"  CSV: {config.CSV_FILE}")
    print(f"  Images: {config.SAVED_PLATES_DIR}/")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
"""
Configuration File for Number Plate Recognition System
Centralized settings for easy customization
"""

import os

# ==================== PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tesseract Configuration
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# TESSERACT_PATH = '/usr/local/bin/tesseract'  # Mac
# TESSERACT_PATH = '/usr/bin/tesseract'  # Linux

# Model Paths
CASCADE_PATH = os.path.join(BASE_DIR, 'models', 'haarcascade_russian_plate_number.xml')

# Storage Paths
SAVED_PLATES_DIR = os.path.join(BASE_DIR, 'saved_plates')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')

# File Names
DATABASE_FILE = os.path.join(DATABASE_DIR, 'plates.db')
CSV_FILE = os.path.join(EXPORTS_DIR, 'detected_plates.csv')
LOG_FILE = os.path.join(EXPORTS_DIR, 'detection_log.txt')

# ==================== DETECTION SETTINGS ====================
# Plate Size Constraints
MIN_PLATE_AREA = 3000      # Minimum area (pixels²)
MAX_PLATE_AREA = 50000     # Maximum area (pixels²)
MIN_PLATE_WIDTH = 100      # Minimum width (pixels)
MIN_PLATE_HEIGHT = 30      # Minimum height (pixels)

# Detection Parameters
CASCADE_SCALE_FACTOR = 1.1  # How much image size is reduced at each scale
CASCADE_MIN_NEIGHBORS = 5   # How many neighbors each rectangle should have
FRAME_SKIP = 1              # Process every Nth frame (1 = all frames)

# ==================== OCR SETTINGS ====================
CONFIDENCE_THRESHOLD = 0.6      # Minimum confidence to accept (0.0 - 1.0)
AUTO_SAVE_THRESHOLD = 0.8       # Auto-save if confidence above this
MIN_PLATE_LENGTH = 4            # Minimum characters in plate
MAX_PLATE_LENGTH = 10           # Maximum characters in plate

# OCR Configurations
OCR_CONFIG_PSM7 = '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
OCR_CONFIG_PSM8 = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
OCR_CONFIG_PSM13 = '--psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

# ==================== SYSTEM SETTINGS ====================
# Duplicate Prevention
DUPLICATE_TIME_WINDOW = 5       # Seconds to ignore duplicate detections

# Camera Settings
CAMERA_INDEX = 0                # 0 for default camera, 1 for external
CAMERA_WIDTH = 1280             # Camera resolution width
CAMERA_HEIGHT = 720             # Camera resolution height
CAMERA_FPS = 30                 # Target FPS

# Performance
MAX_DETECTION_TIME = 1.0        # Maximum time per detection (seconds)
PERFORMANCE_BUFFER_SIZE = 30    # Number of frames to average for FPS

# ==================== UI SETTINGS ====================
# Colors (BGR format)
COLOR_HIGH_CONFIDENCE = (0, 255, 0)      # Green
COLOR_LOW_CONFIDENCE = (0, 165, 255)     # Orange
COLOR_DASHBOARD_BG = (0, 0, 0)           # Black
COLOR_TEXT = (255, 255, 255)             # White
COLOR_ROI = (255, 0, 255)                # Magenta

# UI Elements
DASHBOARD_WIDTH = 400
DASHBOARD_HEIGHT = 180
BOX_THICKNESS = 3
TEXT_FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
TEXT_SIZE = 0.7
TEXT_THICKNESS = 2

# ==================== LOGGING SETTINGS ====================
LOG_LEVEL = 'INFO'              # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_TO_CONSOLE = True

# ==================== FEATURES TOGGLE ====================
ENABLE_AUTO_SAVE = False        # Start with auto-save enabled
ENABLE_DASHBOARD = True         # Show dashboard by default
ENABLE_ROI_MODE = False         # Enable ROI selection
ENABLE_STATISTICS = True        # Track and show statistics
ENABLE_DUPLICATE_CHECK = True   # Prevent duplicate saves

# ==================== DATABASE SETTINGS ====================
DB_VACUUM_ON_START = False      # Clean database on startup
DB_BACKUP_ON_EXIT = True        # Backup database on exit
MAX_RECORDS = 10000             # Maximum records before auto-cleanup

# ==================== VALIDATION ====================
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check if Tesseract exists
    if not os.path.exists(TESSERACT_PATH):
        errors.append(f"Tesseract not found at: {TESSERACT_PATH}")
    
    # Check if cascade file exists
    if not os.path.exists(CASCADE_PATH):
        errors.append(f"Cascade file not found at: {CASCADE_PATH}")
    
    # Check value ranges
    if not (0.0 <= CONFIDENCE_THRESHOLD <= 1.0):
        errors.append("CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")
    
    if not (0.0 <= AUTO_SAVE_THRESHOLD <= 1.0):
        errors.append("AUTO_SAVE_THRESHOLD must be between 0.0 and 1.0")
    
    if FRAME_SKIP < 1:
        errors.append("FRAME_SKIP must be at least 1")
    
    return errors

# ==================== DIRECTORY CREATION ====================
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        SAVED_PLATES_DIR,
        DATABASE_DIR,
        EXPORTS_DIR,
        os.path.join(BASE_DIR, 'models'),
        os.path.join(BASE_DIR, 'utils'),
        os.path.join(BASE_DIR, 'tests'),
        os.path.join(BASE_DIR, 'docs')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ All directories created/verified")

# ==================== INITIALIZATION ====================
if __name__ == "__main__":
    print("Configuration Validation")
    print("=" * 50)
    
    # Validate configuration
    errors = validate_config()
    
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Configuration is valid")
    
    # Create directories
    create_directories()
    
    print("\nConfiguration Summary:")
    print(f"  Tesseract: {TESSERACT_PATH}")
    print(f"  Cascade: {CASCADE_PATH}")
    print(f"  Database: {DATABASE_FILE}")
    print(f"  CSV Export: {CSV_FILE}")
    print(f"  Confidence Threshold: {CONFIDENCE_THRESHOLD}")
    print(f"  Auto-save Threshold: {AUTO_SAVE_THRESHOLD}")
    print("=" * 50)
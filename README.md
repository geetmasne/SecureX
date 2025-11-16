SecureX: Real-time Automatic Number Plate Recognition (ANPR) System

SecureX is a powerful AI-driven real-time Automatic Number Plate Recognition (ANPR) system designed to enhance modern security and access control. By combining Python, OpenCV, and Tesseract, it automates the entire process of detecting, reading, and recording vehicle license plates with high accuracy and speed. This eliminates slow, error-prone manual checking and ensures reliable monitoring at checkpoints, gates, societies, campuses, and parking areas. SecureX not only strengthens security by instantly identifying unauthorized or suspicious vehicles but also creates a complete digital record of all entries through automated SQLite and CSV logging. Its ability to operate continuously, analyze live video feeds, and generate tamper-proof data makes it an essential solution for smart surveillance, efficient traffic management, and future-ready smart city systems.

Features

Real-Time Detection: Identifies license plates from a live webcam feed.

Haar Cascade Classifier: Uses OpenCV's robust Haar Cascade for initial plate region detection.

Smart OCR Engine: Improves accuracy by applying multiple preprocessing techniques (Adaptive Thresholding, Otsu's Binarization, CLAHE) and choosing the best OCR result.

Data Persistence: Saves all confirmed detections to an SQLite database (plates.db).

CSV Export: Automatically logs detections to a .csv file for easy analysis in Excel or other tools.

Duplicate Prevention: A built-in manager prevents saving the same plate number multiple times within a short window.

On-Screen Dashboard: Displays real-time stats like FPS (Frames Per Second), total detections, and unique plates found today.

Highly Configurable: All settings (camera index, detection parameters, confidence thresholds, paths) are managed in a single config.py file.

How It Works

The application follows a simple pipeline:

Capture: Reads a frame from the webcam.

Detect: Uses a pre-trained Haar Cascade classifier (haarcascade_russian_plate_number.xml) to find rectangular areas that might be license plates.

Filter: Filters these areas based on size constraints (min/max area) defined in config.py.

Preprocess: For each potential plate, it creates multiple processed versions (Grayscale, Adaptive Threshold, Otsu Threshold) to handle different lighting conditions.

Recognize (OCR): Runs Tesseract OCR on each processed image to extract text.

Validate: The best text result is chosen based on confidence. It's then validated against format rules (e.g., min/max length, allowed characters) from config.py.

Display: Draws a bounding box around the validated plate and displays the recognized number and confidence.

Save: If auto-save is on (or the user manually saves), the plate number, timestamp, confidence, and a cropped image of the plate are saved to the database and CSV file.

📊 Execution Flow Diagram

┌─────────────────────────────────────────┐
│          START APPLICATION              │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│     Load Configuration (config.py)      │
│  - Paths, Settings, Thresholds          │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│     Validate Configuration              │
│  - Check Tesseract path                 │
│  - Check cascade file                   │
│  - Validate settings                    │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│       Initialize Components             │
│  - Database                             │
│  - OCR Engine                           │
│  - Duplicate Manager                    │
│  - Performance Monitor                  │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│             Open Camera                 │
│  - Set resolution                       │
│  - Set FPS                              │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         MAIN LOOP (Continuous)          │
└───────────────┬─────────────────────────┘
                │
                ▼
      ┌───────────────────────────────┐
      │     1. Capture Frame          │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │       2. Skip Frames          │
      │      (if FRAME_SKIP>1)        │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │  3. Convert to Grayscale      │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │ 4. Detect Plates (Cascade)    │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │ 5. For Each Detected Plate:   │
      │   - Filter by size            │
      │   - Extract region            │
      │   - Preprocess image          │
      │   - Run OCR (multiple methods)│
      │   - Validate text             │
      │   - Check confidence          │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │  6. Draw Detection Box        │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │ 7. Auto-save (if enabled)     │
      │   - Check duplicate           │
      │   - Save image                │
      │   - Save to database          │
      │   - Save to CSV               │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │     8. Draw Dashboard         │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │     9. Display Frame          │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │ 10. Handle Keyboard Input     │
      │   Q - Quit                    │
      │   A - Toggle Auto-save        │
      │   D - Toggle Dashboard        │
      │   S - Manual Save             │
      └─────────────┬─────────────────┘
                    │
                    ▼
      ┌───────────────────────────────┐
      │       Quit Pressed?           │
      └─────────────┬─────────────────┘
        No          │         Yes
        │           │
        ▼           ▼
   (Continue)   ┌───────────────────────────┐
                │ Cleanup & Summary         │
                │ - Release camera          │
                │ - Close windows           │
                │ - Show statistics         │
                └───────────────────────────┘


🚀 Setup and Installation Guide

Follow these steps carefully to get the project running.

Step 1: Prerequisites (Crucial!)

This project depends on Google's Tesseract-OCR engine. You must install it on your computer before running the Python script.

Windows:

Download the installer from tesseract-ocr-w64-setup.

Run the installer. Important: When installing, make sure to check the box to add Tesseract to your system's PATH.

Note the installation path (e.g., C:\Program Files\Tesseract-OCR). You will need this for Step 4.

macOS (using Homebrew):

brew install tesseract

Linux (Ubuntu/Debian):

sudo apt update
sudo apt install tesseract-ocr

Step 2: Get the Haar Cascade Model

The project is configured to use a model for detecting Russian license plates, but this model file (.xml) is not included.

Create a new folder in your project directory named models.

Go to the OpenCV Haar Cascades repository.

Find the file haarcascade_russian_plate_number.xml.

Download this file and place it inside the models folder you just created.

Project structure should now look like this:

NumberPlateRecognition/
│
├── 📄 main.py                          # Main file
├── 📄 requirements.txt                 # Python dependencies
├── 📄 config.py                        # Configuration file
├── 📄 README.md                        # Project documentation
│
├── 📂 models/
│   └── haarcascade_russian_plate_number.xml  # Cascade classifier
│
├── 📂 saved_plates/                    # Auto-created - stores plate images
│   ├── plate_20251115_143022.jpg
│   ├── plate_20251115_143145.jpg
│   └── ...
│
├── 📂 database/                        # Auto-created - database files
│   └── plates.db                       # SQLite database
│
└── 📂 exports/                         # Auto-created - exported data
    └── detected_plates.csv             # CSV export
  

Step 3: Set up Python Environment & Install Libraries

It is highly recommended to use a Python virtual environment to avoid conflicts with other projects.

Create a virtual environment:

python -m venv venv

Activate the environment:

On Windows: .\venv\Scripts\activate

On macOS/Linux: source vVenv/bin/activate

Install the required libraries:

pip install -r requirements.txt

Step 4: Configure the Project (Very Important!)

Open the config.py file with any text editor.

Set Tesseract Path: Find the TESSERACT_PATH variable. You must change this to point to the tesseract.exe file you installed in Step 1.

Windows: The path might be r'C:\Program Files\Tesseract-OCR\tesseract.exe' (this is the default in the file, but double-check your installation).

macOS: Run which tesseract in your terminal to find the path (e.g., r'/usr/local/bin/tesseract').

Linux: Run which tesseract in your terminal to find the path (e.g., r'/usr/bin/tesseract').

(Optional) Change Camera: If your webcam is not the default, change CAMERA_INDEX = 0 to CAMERA_INDEX = 1 (or another number).

🏃‍♂️ Running the Application

After completing all setup steps, simply run the main.py script from your activated virtual environment:

python main.py

A window should open showing your webcam feed. When a license plate is detected, a box will appear around it.

Controls

[A] : Toggle Auto-Save. When ON, the system automatically saves any plate with confidence above the AUTO_SAVE_THRESHOLD (set in config.py).

[S] or [Spacebar] : Manual Save. Instantly saves the highest-confidence plate currently on screen, regardless of confidence.

[D] : Toggle Dashboard. Hides or shows the statistics panel in the top-left corner.

[Q] : Quit. Stops the program and closes the window.

📁 Project File Structure

.
├── config.py                 # Configuration
├── main.py                   # Application logic
├── requirements.txt          # Dependencies
│
├── models/
│   └── haarcascade_russian_plate_number.xml
│
├── database/
│   └── plates.db
│
├── exports/
│   └── detected_plates.csv
│
└── saved_plates/
    └── plate_YYYYMMDD_HHMMSS.jpg



⚠️ Troubleshooting

Error: Tesseract not found at...

This is the most common error. It means the TESSERACT_PATH in config.py is incorrect. Go back to Step 5 and make sure the path points exactly to the tesseract.exe file (on Windows) or the tesseract binary (on macOS/Linux).

Error: Cannot load cascade from...

This means the haarcascde_russian_plate_number.xml file is missing or in the wrong place. Make sure you created the models folder and placed the .xml file inside it, as described in Step 3.

Camera window opens but is blank/black:

Your camera is not being detected. Try changing CAMERA_INDEX in config.py from 0 to 1 or 2.

Detection is not very accurate:

ANPR is highly dependent on camera quality, lighting, and the angle of the plate.

Try improving the lighting in your room.

You can "tune" the detection by adjusting CASCADE_SCALE_FACTOR and CASCADE_MIN_NEIGHBORS in config.py.
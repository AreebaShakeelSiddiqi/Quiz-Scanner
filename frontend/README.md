# QuizScan — Automated Quiz Scanner & Grading System

An AI-powered full-stack web application that automatically scans, reads, and grades bubble-sheet quiz papers using computer vision and OCR.

---

## Tasks Completed

- ✅ **Task 1 — QR Code Decoding:** Decodes answer key embedded in QR code on each quiz sheet using pyzbar + OpenCV. Supports multiple scales and rotations for robustness.
- ✅ **Task 2 — Student Info Extraction:** Extracts student name and registration number from the sheet header using Tesseract OCR.
- ✅ **Task 3 — Bubble Sheet Reading:** Detects and reads filled bubbles for Part-I and Part-II (8 questions each) using HoughCircles + contour detection with table border removal.
- ✅ **Task 4 — Quiz Grading:** Compares student answers against the decoded answer key, computes score, percentage, and letter grade with per-question breakdown.
- ✅ **Task 5 — Batch Processing & Report Export:** Processes multiple quiz sheets at once and exports results to Excel (.xlsx) with class statistics summary.

---

## Libraries & Frameworks Used

### Backend
| Library | Purpose |
|---|---|
| Flask | REST API server |
| flask-cors | Cross-origin request handling |
| OpenCV (cv2) | Image processing, circle detection, morphological operations |
| pyzbar | QR code decoding |
| pytesseract | OCR for student name/reg extraction |
| pdf2image | PDF to image conversion |
| pandas | Data manipulation and Excel export |
| openpyxl | Excel file generation |
| numpy | Numerical operations for image arrays |
| Pillow | Image saving and format conversion |

### Frontend
| Library | Purpose |
|---|---|
| React | UI framework |
| axios | HTTP requests to backend API |
| App.css | Custom dark-theme styling |

---

## How to Install and Run

### Prerequisites
- macOS (M1/M2/Intel)
- Python 3.11+
- Node.js 18+
- Homebrew

### System Dependencies
```bash
brew install python@3.11 node tesseract zbar poppler
```

### Backend Setup
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install flask flask-cors opencv-python-headless pillow pyzbar pytesseract pandas openpyxl numpy pdf2image
python app.py
```

Backend runs on: `http://localhost:5001`

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

Frontend runs on: `http://localhost:3000`

---

## How to Use

### Single Quiz Mode
1. Open `http://localhost:3000` in your browser
2. Select **Single Quiz** tab
3. Upload a quiz sheet image (JPG, PNG) or scanned PDF
4. Click **Scan & Grade**
5. View results — student info, answer key from QR, per-question breakdown, and final grade

### Batch Processing Mode
1. Select **Batch Processing** tab
2. Enter a quiz name
3. Upload multiple quiz sheet images
4. Click **Process Batch**
5. View class results table and download Excel report

### Reports
- Every scan automatically saves to the **Reports** tab
- View history with timestamps, scores, and grades
- Download full Excel report of all scans
- Clear history with the Clear All button

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/process` | Process single quiz image |
| POST | `/api/batch` | Process multiple images |
| GET | `/api/reports` | Get all saved reports |
| GET | `/api/reports/excel` | Download reports as Excel |
| DELETE | `/api/reports/clear` | Clear all reports |
| GET | `/api/download/<filename>` | Download batch Excel file |

---

## Project Structure
quiz-scanner/
├── backend/
│   ├── app.py              # Flask API server
│   ├── qr_decoder.py       # Task 1 — QR code decoding
│   ├── ocr_extractor.py    # Task 2 — Student info OCR
│   ├── bubble_reader.py    # Task 3 — Bubble sheet reading
│   ├── grader.py           # Task 4 — Quiz grading logic
│   ├── batch.py            # Task 5 — Batch processing
│   └── uploads/            # Temporary uploaded files
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React application
│   │   └── App.css         # Dark theme styling
│   └── public/
├── output/                 # Generated Excel reports + reports.json
└── README.md
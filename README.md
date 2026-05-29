````md
# QuizScan — Automated Quiz Scanner & Grading System

An AI-powered full-stack web application that automatically scans, reads, and grades bubble-sheet quiz papers using Computer Vision and OCR.

---

## 🚀 Live Demo

🔗 [View Web App](YOUR_DEPLOYED_LINK_HERE)

> No installation required — simply open the web app and start scanning quiz sheets instantly.

---

## ✅ Tasks Completed

- ✅ **Task 1 — QR Code Decoding:** Decodes answer key embedded in QR code on each quiz sheet using pyzbar + OpenCV. Supports multiple scales and rotations for robustness.

- ✅ **Task 2 — Student Info Extraction:** Extracts student name and registration number from the sheet header using Tesseract OCR.

- ✅ **Task 3 — Bubble Sheet Reading:** Detects and reads filled bubbles for Part-I and Part-II (8 questions each) using HoughCircles + contour detection with table border removal.

- ✅ **Task 4 — Quiz Grading:** Compares student answers against the decoded answer key, computes score, percentage, and letter grade with per-question breakdown.

- ✅ **Task 5 — Batch Processing & Report Export:** Processes multiple quiz sheets at once and exports results to Excel (.xlsx) with class statistics summary.

---

# 🛠️ Libraries & Frameworks Used

## Backend

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

---

## Frontend

| Library | Purpose |
|---|---|
| React | UI framework |
| axios | HTTP requests to backend API |
| App.css | Custom dark-theme styling |

---

# 📖 How to Use

## Single Quiz Mode

1. Open the deployed web app in your browser
2. Select **Single Quiz** tab
3. Upload a quiz sheet image (JPG, PNG) or scanned PDF
4. Click **Scan & Grade**
5. View results — student info, answer key from QR, per-question breakdown, and final grade

---

## Batch Processing Mode

1. Select **Batch Processing** tab
2. Enter a quiz name
3. Upload multiple quiz sheet images
4. Click **Process Batch**
5. View class results table and download Excel report

---

## Reports

- Every scan automatically saves to the **Reports** tab
- View history with timestamps, scores, and grades
- Download full Excel report of all scans
- Clear history with the Clear All button

---

# 📡 API Endpoints

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

# 📁 Project Structure

```bash
quiz-scanner/
├── backend/
│   ├── app.py
│   ├── qr_decoder.py
│   ├── ocr_extractor.py
│   ├── bubble_reader.py
│   ├── grader.py
│   ├── batch.py
│   └── uploads/
│
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── App.css
│   └── public/
│
├── output/
└── README.md
````

---

# ⚙️ How It Works

1. **Upload** — User uploads a quiz sheet (image or PDF)

2. **QR Decode** — System finds and decodes the QR code to extract the answer key (Set, Part-I answers, Part-II answers)

3. **OCR** — Tesseract reads the student name and registration number from the top of the sheet

4. **Bubble Detection** — OpenCV detects all answer bubbles using:

   * Table border removal via morphological operations
   * HoughCircles for lightly filled bubbles
   * Contour detection for fully filled/dark bubbles
   * Grid-based clustering to map bubbles to correct question rows and option columns

5. **Grading** — Student answers compared against key and score calculated

6. **Report** — Results saved to JSON history and available as Excel download

---

# 📸 Screenshots

## Scanner Page

![Scanner](demo/screenshot_scanner.png)

---

## Results Page

![Results](demo/screenshot_results.png)

---

## Reports Page

![Reports](demo/screenshot_reports.png)

---

# 🔮 Future Improvements

* Handwritten answer recognition
* Teacher/Admin authentication system
* Cloud database integration
* AI-based answer confidence scoring
* Mobile responsive optimization

---

# 👩‍💻 Author

**Areeba Shakeel Siddiqi**

🔗 Portfolio: https://areebashakeelsiddiqi.github.io/My-portfolio/

```
```

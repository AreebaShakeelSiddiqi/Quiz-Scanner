# Task 2 — Student Info Extraction
import cv2
import numpy as np
import pytesseract
import re

def extract_student_info(image_path):
    """Extract student name and registration number using OCR."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Name and Reg# are typically in top portion of the sheet
    top_region = gray[:int(h*0.25), :]
    
    # Preprocess for better OCR
    denoised = cv2.fastNlMeansDenoising(top_region, h=10)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # OCR the top region
    config = '--psm 6 --oem 3'
    text = pytesseract.image_to_string(thresh, config=config)
    
    name = ""
    reg_no = ""
    
    for line in text.split('\n'):
        line = line.strip()
        # Look for Name field
        if re.search(r'name\s*[:\-]?\s*(.+)', line, re.IGNORECASE):
            match = re.search(r'name\s*[:\-]?\s*(.+)', line, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
        # Look for Registration/Reg field
        elif re.search(r'reg(istration)?\s*(no|#|num)?\s*[:\-]?\s*(.+)', line, re.IGNORECASE):
            match = re.search(r'reg(istration)?\s*(no|#|num)?\s*[:\-]?\s*(.+)', line, re.IGNORECASE)
            if match:
                reg_no = match.group(3).strip()
    
    # Fallback: try full-page OCR
    if not name and not reg_no:
        full_text = pytesseract.image_to_string(img, config=config)
        for line in full_text.split('\n'):
            if 'name' in line.lower() and ':' in line:
                name = line.split(':', 1)[-1].strip()
            if 'reg' in line.lower() and ('#' in line or ':' in line):
                reg_no = re.sub(r'[^\w\-/]', '', line.split(':', 1)[-1].strip())
    
    return {
        "name": name or "Unknown",
        "reg_no": reg_no or "Unknown"
    }
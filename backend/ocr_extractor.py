import cv2
import base64
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

def extract_student_info(image_path):
    api_key = os.getenv("GOOGLE_VISION_API_KEY")
    vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    h, w = img.shape[:2]
    header = img[:int(h * 0.22), :]

    _, buf = cv2.imencode('.jpg', header, [cv2.IMWRITE_JPEG_QUALITY, 95])
    b64 = base64.standard_b64encode(buf.tobytes()).decode('utf-8')

    try:
        payload = {
            "requests": [{
                "image": {"content": b64},
                "features": [{"type": "TEXT_DETECTION"}]
            }]
        }
        res = requests.post(vision_url, json=payload, timeout=10)
        print(f"DEBUG RESPONSE: {res.text}")
        data = res.json()

        full_text = data['responses'][0].get('fullTextAnnotation', {}).get('text', '')
        if not full_text:
            full_text = ' '.join(
                a['description']
                for a in data['responses'][0].get('textAnnotations', [])[1:]
            )

        name   = _extract_name(full_text)
        reg_no = _extract_reg(full_text)

    except Exception as e:
        print(f"Google Vision error: {e}")
        name, reg_no = "Unknown", "Unknown"

    return {
        "name":   name   or "Unknown",
        "reg_no": reg_no or "Unknown"
    }


def _extract_name(text):
    for line in text.split('\n'):
        m = re.search(r'name\s*[:\-]?\s*(.+)', line, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            val = re.sub(r'[^\w\s\-\.]', '', val).strip()
            if len(val) > 2:
                return val
    return ""


def _extract_reg(text):
    m = re.search(r'([A-Z]{2,}-[A-Z]{2,}\d{2,}-\d{2,})', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    for line in text.split('\n'):
        m = re.search(r'reg(?:istration)?\s*[#no.:]*\s*[:\-]?\s*([A-Z0-9][\w\-]+)', line, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""
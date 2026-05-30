import cv2
import base64
import requests
import re
import os

def extract_student_info(image_path):
    # Fetch directly from the system environment (works perfectly on Railway & Local if configured)
    api_key = os.environ.get("GOOGLE_VISION_API_KEY")
    
    if not api_key:
        print("CRITICAL ERROR: GOOGLE_VISION_API_KEY environment variable is missing!")
        return {"name": "Missing API Key", "reg_no": "Missing API Key"}
        
    vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"CRITICAL ERROR: Cannot read image path: {image_path}")
        return {"name": "Invalid Image", "reg_no": "Invalid Image"}

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
        
        # If Google rejects the API key or has an error, capture it safely without crashing
        if res.status_code != 200:
            print(f"Google Vision API Error Status {res.status_code}: {res.text}")
            return {"name": "API Error", "reg_no": "API Error"}

        data = res.json()
        responses = data.get('responses', [{}])
        
        full_text = responses[0].get('fullTextAnnotation', {}).get('text', '')
        if not full_text:
            full_text = ' '.join(
                a['description']
                for a in responses[0].get('textAnnotations', [])[1:]
            )

        name   = _extract_name(full_text)
        reg_no = _extract_reg(full_text)

    except Exception as e:
        print(f"Google Vision internal exception caught safely: {e}")
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
    # Matches patterns like BSE-JFA2Y-04F, BSE-4A-123, etc.
    m = re.search(r'([A-Z0-9]{2,4}-[A-Z0-9]{2,5}-\d{2,4})', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
        
    for line in text.split('\n'):
        m = re.search(r'reg(?:istration)?\s*[#no.:]*\s*[:\-]?\s*([A-Z0-9][\w\-]+)', line, re.IGNORECASE)
        if m:
            return m.group(1).strip().upper()
    return ""
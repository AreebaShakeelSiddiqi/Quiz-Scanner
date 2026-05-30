import cv2
import base64
import requests
import re
import os

def extract_student_info(image_path):
    """
    Super-safe student info extraction. 
    Guaranteed never to crash the main application thread.
    """
    # Initialize default safe dictionary
    default_response = {"name": "Unknown", "reg_no": "Unknown"}
    
    try:
        # 1. Check if file exists
        if not os.path.exists(image_path):
            print(f"CRITICAL ERROR: Image path does not exist: {image_path}")
            return default_response

        # 2. Try to read the image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            print(f"CRITICAL ERROR: OpenCV cv2.imread returned None for: {image_path}")
            return default_response

        h, w = img.shape[:2]
        header = img[:int(h * 0.22), :]

        # 3. Encode image to Base64
        success, buf = cv2.imencode('.jpg', header, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not success:
            print("CRITICAL ERROR: cv2.imencode failed to process header snippet")
            return default_response
            
        b64 = base64.standard_b64encode(buf.tobytes()).decode('utf-8')

        # 4. Check for API key safely
        # Railway injects environment variables without needing load_dotenv()
        api_key = os.environ.get("GOOGLE_VISION_API_KEY")
        if not api_key:
            print("CRITICAL ERROR: GOOGLE_VISION_API_KEY is not set in Railway environment variables!")
            return {"name": "Missing Key", "reg_no": "Missing Key"}

        vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
        
        payload = {
            "requests": [{
                "image": {"content": b64},
                "features": [{"type": "TEXT_DETECTION"}]
            }]
        }

        # 5. Make the external request with an explicit timeout handler
        try:
            res = requests.post(vision_url, json=payload, timeout=10)
        except requests.exceptions.RequestException as req_err:
            print(f"Google Vision network/timeout request failed: {req_err}")
            return default_response

        if res.status_code != 200:
            print(f"Google Vision API Error Status {res.status_code}: {res.text}")
            return {"name": "API Refused", "reg_no": "API Refused"}

        data = res.json()
        responses = data.get('responses', [{}])
        if not responses or not isinstance(responses, list):
            return default_response

        full_text = responses[0].get('fullTextAnnotation', {}).get('text', '')
        if not full_text:
            text_annotations = responses[0].get('textAnnotations', [])
            if len(text_annotations) > 1:
                full_text = ' '.join(a.get('description', '') for a in text_annotations[1:])

        name = _extract_name(full_text)
        reg_no = _extract_reg(full_text)

        return {
            "name": name or "Unknown",
            "reg_no": reg_no or "Unknown"
        }

    except Exception as global_err:
        # Catch absolutely anything else to prevent a 500 internal application crash
        print(f"CRITICAL OVERALL OCR CRASH CAUGHT: {global_err}")
        return default_response


def _extract_name(text):
    if not text:
        return ""
    for line in text.split('\n'):
        m = re.search(r'name\s*[:\-]?\s*(.+)', line, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            val = re.sub(r'[^\w\s\-\.]', '', val).strip()
            if len(val) > 2:
                return val
    return ""


def _extract_reg(text):
    if not text:
        return ""
    # Looks for a registration format sequence like letters-numbers/letters-numbers
    m = re.search(r'([A-Z0-9]{2,4}-[A-Z0-9]{2,5}-\d{2,4})', text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
        
    for line in text.split('\n'):
        m = re.search(r'reg(?:istration)?\s*[#no.:]*\s*[:\-]?\s*([A-Z0-9][\w\-]+)', line, re.IGNORECASE)
        if m:
            return m.group(1).strip().upper()
    return ""
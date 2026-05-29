# Task 1 — QR Code Decoding
import cv2
import numpy as np
from pyzbar import pyzbar
import re

def decode_answer_key(image_path):
    """Decode QR code from quiz image and return structured answer key."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    # Try multiple scales and rotations for robustness
    for scale in [1.0, 1.5, 0.75, 2.0]:
        resized = cv2.resize(img, None, fx=scale, fy=scale)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        for angle in [0, 5, -5, 10, -10]:
            if angle != 0:
                h, w = gray.shape
                M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
                rotated = cv2.warpAffine(gray, M, (w, h))
            else:
                rotated = gray
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(rotated)
            
            decoded = pyzbar.decode(enhanced)
            if decoded:
                payload = decoded[0].data.decode('utf-8')
                return parse_qr_payload(payload)
    
    raise ValueError("QR code not found in image")

def parse_qr_payload(payload):
    """
    Parse payload like:
    AI Quiz SP2026 Set-C | Part-I: Q1=D Q2=A ... | Part-II: Q1=C Q2=D ...
    """
    result = {
        "set": "",
        "class": "",
        "subject": "",
        "part1": {},
        "part2": {}
    }
    
    # Extract set identifier
    set_match = re.search(r'Set-?(\w+)', payload, re.IGNORECASE)
    if set_match:
        result["set"] = set_match.group(1)
    
    # Extract subject/class from beginning
    header = payload.split('|')[0].strip()
    result["subject"] = header
    
    # Extract Part-I answers
    part1_match = re.search(r'Part-?I[^I]?:(.*?)(?:\||$)', payload, re.IGNORECASE)
    if part1_match:
        answers_str = part1_match.group(1)
        for m in re.finditer(r'Q(\d+)=([A-D])', answers_str, re.IGNORECASE):
            result["part1"][f"Q{int(m.group(1)):02d}"] = m.group(2).upper()
    
    # Extract Part-II answers
    part2_match = re.search(r'Part-?II:(.*?)(?:\||$)', payload, re.IGNORECASE)
    if part2_match:
        answers_str = part2_match.group(1)
        for m in re.finditer(r'Q(\d+)=([A-D])', answers_str, re.IGNORECASE):
            result["part2"][f"Q{int(m.group(1)):02d}"] = m.group(2).upper()
    
    return result
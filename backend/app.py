from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, traceback, json
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from qr_decoder import decode_answer_key
from ocr_extractor import extract_student_info
from bubble_reader import read_bubble_sheet
from grader import grade_quiz
from batch import process_batch

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'output')
REPORTS_FILE  = os.path.join(OUTPUT_FOLDER, 'reports.json')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    if filename.lower().endswith('.pdf'):
        images   = convert_from_path(filepath, dpi=200)
        img_path = filepath.replace('.pdf', '_page1.jpg')
        images[0].save(img_path, 'JPEG')
        return img_path
    return filepath

def save_report(data):
    try:
        reports = []
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r') as f:
                reports = json.load(f)
        reports.append(data)
        with open(REPORTS_FILE, 'w') as f:
            json.dump(reports, f, indent=2)
    except Exception as e:
        print(f"Report save error: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/reports', methods=['GET'])
def get_reports():
    try:
        if os.path.exists(REPORTS_FILE):
            with open(REPORTS_FILE, 'r') as f:
                return jsonify(json.load(f))
        return jsonify([])
    except:
        return jsonify([])

@app.route('/api/reports/clear', methods=['DELETE'])
def clear_reports():
    try:
        if os.path.exists(REPORTS_FILE):
            os.remove(REPORTS_FILE)
        return jsonify({"status": "cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/excel', methods=['GET'])
def download_reports_excel():
    try:
        if not os.path.exists(REPORTS_FILE):
            return jsonify({"error": "No reports yet"}), 404
        with open(REPORTS_FILE, 'r') as f:
            reports = json.load(f)
        rows = []
        for r in reports:
            row = {
                "Timestamp":   r.get("timestamp",""),
                "Name":        r.get("student",{}).get("name",""),
                "Reg No":      r.get("student",{}).get("reg_no",""),
                "Set":         r.get("set",""),
                "Subject":     r.get("subject",""),
                "Score":       f"{r.get('score',0)}/{r.get('total',16)}",
                "Percentage":  r.get("percentage",0),
                "Grade":       r.get("grade",""),
                "Correct":     r.get("correct",0),
                "Incorrect":   r.get("incorrect",0),
                "Unattempted": r.get("unattempted",0),
            }
            # Add individual question answers
            for q in [f"Q{i:02d}" for i in range(1,9)]:
                row[f"P1_{q}"] = r.get("part1",{}).get(q,"")
                row[f"P2_{q}"] = r.get("part2",{}).get(q,"")
            rows.append(row)
        df = pd.DataFrame(rows)
        filepath = os.path.join(OUTPUT_FOLDER, 'reports_export.xlsx')
        df.to_excel(filepath, index=False)
        return send_file(filepath, as_attachment=True,
                        download_name='QuizScan_Reports.xlsx')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_single():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    file = request.files['image']
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use JPG, PNG or PDF"}), 400
    try:
        filepath = save_upload(file)
    except Exception as e:
        return jsonify({"error": f"File save failed: {str(e)}"}), 500

    result = {"filename": file.filename, "errors": {}}

    try:
        result["answer_key"] = decode_answer_key(filepath)
    except Exception as e:
        result["answer_key"] = None
        result["errors"]["qr"] = str(e)

    try:
        result["student_info"] = extract_student_info(filepath)
    except Exception as e:
        result["student_info"] = {"name": "Unknown", "reg_no": "Unknown"}
        result["errors"]["ocr"] = str(e)

    try:
        result["student_answers"] = read_bubble_sheet(filepath)
    except Exception as e:
        result["student_answers"] = {"part1": {}, "part2": {}}
        result["errors"]["bubble"] = str(e)

    if result["answer_key"] and result["student_answers"]:
        result["grade_report"] = grade_quiz(
            result["student_answers"], result["answer_key"])
    else:
        result["grade_report"] = None

    gr = result.get("grade_report") or {}
    si = result.get("student_info") or {}
    ak = result.get("answer_key") or {}
    save_report({
        "timestamp":   datetime.now().isoformat(),
        "filename":    file.filename,
        "student":     {"name": si.get("name","Unknown"), "reg_no": si.get("reg_no","Unknown")},
        "set":         ak.get("set",""),
        "subject":     ak.get("subject",""),
        "grade":       gr.get("grade",""),
        "score":       gr.get("total_marks",0),
        "total":       gr.get("total_questions",16),
        "percentage":  gr.get("percentage",0),
        "correct":     gr.get("correct",0),
        "incorrect":   gr.get("incorrect",0),
        "unattempted": gr.get("unattempted",0),
        "part1":       result.get("student_answers",{}).get("part1",{}),
        "part2":       result.get("student_answers",{}).get("part2",{}),
        "errors":      result.get("errors",{})
    })

    return jsonify(result)

@app.route('/api/batch', methods=['POST'])
def process_batch_route():
    if 'images' not in request.files:
        return jsonify({"error": "No images uploaded"}), 400
    files     = request.files.getlist('images')
    quiz_name = request.form.get('quiz_name', 'Quiz')
    saved_paths = []
    for file in files:
        if file and allowed_file(file.filename):
            try:
                saved_paths.append(save_upload(file))
            except:
                pass
    if not saved_paths:
        return jsonify({"error": "No valid files found"}), 400
    try:
        results, excel_path = process_batch(saved_paths, quiz_name)
        for r in results:
            save_report({
                "timestamp":   datetime.now().isoformat(),
                "filename":    r.get("Quiz",""),
                "student":     {"name": r.get("Name",""), "reg_no": r.get("Reg No","")},
                "set":         r.get("Set",""),
                "subject":     "",
                "grade":       r.get("Grade",""),
                "score":       r.get("Total Marks",0),
                "total":       16,
                "percentage":  r.get("Percentage",0),
                "correct":     r.get("Correct",0),
                "incorrect":   r.get("Incorrect",0),
                "unattempted": r.get("Unattempted",0),
                "part1":       {},
                "part2":       {},
                "errors":      {}
            })
        return jsonify({
            "results":    results,
            "excel_file": os.path.basename(excel_path),
            "count":      len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
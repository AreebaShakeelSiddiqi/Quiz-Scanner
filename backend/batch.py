import os
import pandas as pd
from datetime import datetime
from qr_decoder import decode_answer_key
from ocr_extractor import extract_student_info
from bubble_reader import read_bubble_sheet
from grader import grade_quiz

def process_batch(image_paths, quiz_name="Quiz"):
    rows = []
    for img_path in image_paths:
        row = {"Quiz": quiz_name, "Set": "", "Name": "", "Reg No": ""}
        try:
            ak = decode_answer_key(img_path)
            row["Set"] = ak.get("set", "")
        except:
            ak = {"part1": {}, "part2": {}}
        try:
            si = extract_student_info(img_path)
            row["Name"] = si["name"]
            row["Reg No"] = si["reg_no"]
        except:
            pass
        try:
            sa = read_bubble_sheet(img_path)
        except:
            sa = {"part1": {}, "part2": {}}
        gr = grade_quiz(sa, ak)
        row["Correct"]     = gr["correct"]
        row["Incorrect"]   = gr["incorrect"]
        row["Unattempted"] = gr["unattempted"]
        row["Total Marks"] = gr["total_marks"]
        row["Percentage"]  = gr["percentage"]
        row["Grade"]       = gr["grade"]
        rows.append(row)

    df = pd.DataFrame(rows)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{quiz_name.replace(' ','_')}_{ts}.xlsx")
    df.to_excel(path, index=False)
    return rows, path
# Task 4 — Quiz Grading
def grade_quiz(student_answers, answer_key, negative_marking=0):
    """Compare student answers against answer key and compute grade."""
    report = {
        "part1": {},
        "part2": {},
        "correct": 0,
        "incorrect": 0,
        "unattempted": 0,
        "total_marks": 0,
        "total_questions": 0,
        "percentage": 0,
        "grade": "F"
    }
    
    for part in ["part1", "part2"]:
        student_part = student_answers.get(part, {})
        key_part = answer_key.get(part, {})
        
        all_questions = set(list(student_part.keys()) + list(key_part.keys()))
        
        for q in sorted(all_questions):
            student_ans = student_part.get(q)
            correct_ans = key_part.get(q)
            
            if student_ans is None:
                status = "unattempted"
                report["unattempted"] += 1
            elif student_ans == "INVALID":
                status = "invalid"
                report["incorrect"] += 1
            elif student_ans == correct_ans:
                status = "correct"
                report["correct"] += 1
                report["total_marks"] += 1
            else:
                status = "incorrect"
                report["incorrect"] += 1
                report["total_marks"] -= negative_marking
            
            report[part][q] = {
                "student": student_ans,
                "correct": correct_ans,
                "status": status,
                "symbol": "✓" if status == "correct" else ("✗" if status == "incorrect" else ("?" if status == "invalid" else "—"))
            }
    
    report["total_questions"] = 16  # 8 + 8
    report["total_marks"] = max(0, report["total_marks"])
    report["percentage"] = round((report["total_marks"] / report["total_questions"]) * 100, 1)
    
    # Assign letter grade
    pct = report["percentage"]
    if pct >= 90: report["grade"] = "A+"
    elif pct >= 80: report["grade"] = "A"
    elif pct >= 70: report["grade"] = "B"
    elif pct >= 60: report["grade"] = "C"
    elif pct >= 50: report["grade"] = "D"
    else: report["grade"] = "F"
    
    return report
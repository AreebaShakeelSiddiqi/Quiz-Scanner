import cv2
import numpy as np

def read_bubble_sheet(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = img.shape[:2]

    top    = int(h * 0.18)
    bottom = int(h * 0.42)
    region = gray[top:bottom, :]
    rh, rw = region.shape

    blurred = cv2.GaussianBlur(region, (5, 5), 0)
    thresh  = cv2.threshold(blurred, 0, 255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    clean_thresh = _remove_lines(thresh)

    detected = []

    # Method 1: HoughCircles — catches lightly filled bubbles
    hough = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT,
        dp=1, minDist=18,
        param1=50, param2=22,
        minRadius=12, maxRadius=22
    )
    if hough is not None:
        for (x, y, r) in np.uint16(np.around(hough[0, :])):
            ratio = _fill_ratio(clean_thresh, x, y, r)
            detected.append({
                "x": int(x), "y": int(y), "r": int(r),
                "fill_ratio": ratio
            })

    # Method 2: Contour detection — catches solid black filled bubbles
    contours, _ = cv2.findContours(clean_thresh, cv2.RETR_LIST,
                                    cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        area = cv2.contourArea(c)
        if 200 < area < 2000:
            (x, y), r = cv2.minEnclosingCircle(c)
            peri = cv2.arcLength(c, True)
            if peri == 0:
                continue
            circularity = 4 * np.pi * area / (peri ** 2)
            if circularity > 0.30:
                ratio = _fill_ratio(clean_thresh, x, y, r)
                detected.append({
                    "x": int(x), "y": int(y), "r": int(r),
                    "fill_ratio": ratio
                })

    detected = _deduplicate(detected, 15)

    if len(detected) < 8:
        return _empty_result()

    split_x = rw * 0.485
    p1 = [c for c in detected if c["x"] < split_x]
    p2 = [c for c in detected if c["x"] >= split_x]

    return {
        "part1": _parse_part(p1, label_x_max=320),
        "part2": _parse_part(p2, label_x_max=870)
    }


def _remove_lines(thresh):
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel,
                                iterations=2)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel,
                                iterations=2)
    lines = cv2.add(h_lines, v_lines)
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    lines = cv2.dilate(lines, dilate_kernel, iterations=1)
    return cv2.subtract(thresh, lines)


def _fill_ratio(thresh, x, y, r):
    mask = np.zeros(thresh.shape, np.uint8)
    cv2.circle(mask, (int(x), int(y)), max(int(r)-1, 3), 255, -1)
    area = cv2.countNonZero(mask)
    if area == 0:
        return 0.0
    return cv2.countNonZero(
        cv2.bitwise_and(thresh, thresh, mask=mask)) / area


def _deduplicate(circles, min_d=15):
    keep = []
    for c in sorted(circles, key=lambda x: -x["fill_ratio"]):
        if not any(
            abs(c["x"]-k["x"]) < min_d and abs(c["y"]-k["y"]) < min_d
            for k in keep
        ):
            keep.append(c)
    return keep


def _parse_part(circles, label_x_max, num_q=8, num_opts=4):
    options = ['A', 'B', 'C', 'D']
    result  = {f"Q{i+1:02d}": None for i in range(num_q)}

    bubbles = [c for c in circles if c["x"] > label_x_max]

    if len(bubbles) < num_opts:
        return result

    col_centers = _cluster_1d([c["x"] for c in bubbles], num_opts)
    col_centers = sorted(col_centers)[:num_opts]

    row_centers = _cluster_1d([c["y"] for c in bubbles], num_q)
    row_centers = sorted(row_centers)

    if not col_centers or not row_centers:
        return result

    grid = [[None] * num_opts for _ in range(len(row_centers))]
    for c in bubbles:
        ri = min(range(len(row_centers)),
                 key=lambda i: abs(row_centers[i] - c["y"]))
        ci = min(range(len(col_centers)),
                 key=lambda i: abs(col_centers[i] - c["x"]))
        if ci >= num_opts:
            continue
        if (grid[ri][ci] is None or
                c["fill_ratio"] > grid[ri][ci]["fill_ratio"]):
            grid[ri][ci] = c

    for ri in range(min(len(row_centers), num_q)):
        q_key  = f"Q{ri+1:02d}"
        row    = grid[ri]
        ratios = [cell["fill_ratio"] if cell else 0.0 for cell in row]
        mx     = max(ratios)

        if mx < 0.40:
            result[q_key] = None
        else:
            result[q_key] = options[ratios.index(mx)]

    return result


def _empty_result():
    return {
        "part1": {f"Q{i+1:02d}": None for i in range(8)},
        "part2": {f"Q{i+1:02d}": None for i in range(8)}
    }


def _cluster_1d(values, k):
    if not values:
        return []
    values = sorted(set(int(v) for v in values))
    if len(values) <= k:
        return [float(v) for v in values]
    gaps = sorted(
        range(len(values) - 1),
        key=lambda i: values[i+1] - values[i],
        reverse=True
    )
    splits = set(gaps[:k-1])
    clusters, cur = [], [values[0]]
    for i in range(1, len(values)):
        if (i-1) in splits:
            clusters.append(cur)
            cur = []
        cur.append(values[i])
    clusters.append(cur)
    return [sum(cl) / len(cl) for cl in clusters]
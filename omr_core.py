# omr_core.py
import cv2
import numpy as np
import json
import os
from pathlib import Path

# canonical warp size (you can tune these to your sheet DPI)
CANON_W, CANON_H = 2480, 3508  # A4-like canvas at 300dpi

def order_points(pts):
    rect = np.zeros((4,2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def detect_sheet_corners(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(gray, 50, 150)
    cnts, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*peri, True)
        if len(approx) == 4:
            pts = approx.reshape(4,2)
            return order_points(pts)
    return None

def warp_to_canonical(img, pts):
    dst = np.array([[0,0],[CANON_W-1,0],[CANON_W-1,CANON_H-1],[0,CANON_H-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, M, (CANON_W, CANON_H))
    return warped, M

# load template JSON (created by calibrate.py)
def load_template(template_name):
    p = Path("templates") / f"{template_name}.json"
    if not p.exists():
        raise FileNotFoundError(f"Template not found: {p}")
    with open(p, "r") as f:
        return json.load(f)

def crop_square(img, cx, cy, r=30):
    h, w = img.shape[:2]
    x1, y1 = max(0, cx-r), max(0, cy-r)
    x2, y2 = min(w-1, cx+r), min(h-1, cy+r)
    return img[y1:y2, x1:x2]

def filled_score(cell):
    if cell.size == 0:
        return 0.0
    g = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    # adaptive equalization/contrast may help; keep simple
    _, th = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    fill = np.count_nonzero(th) / th.size
    return float(fill)

def detect_answers_from_warp(warped, template_name, threshold_fill=0.30):
    tpl = load_template(template_name)
    centers = tpl["centers"]  # list of [x,y] ordered by question then choice
    total_questions = tpl["total_questions"]
    choices = tpl["choices"]
    answers = []
    fill_scores = []
    overlay = warped.copy()
    ambiguous = []
    for q in range(total_questions):
        base = q * choices
        scores = []
        for c in range(choices):
            cx, cy = centers[base + c]
            cell = crop_square(warped, int(cx), int(cy), r=28)
            score = filled_score(cell)
            scores.append(score)
        best_idx = int(np.argmax(scores))
        best_score = scores[best_idx]
        # If best score below threshold -> blank
        if best_score >= threshold_fill:
            chosen = best_idx + 1  # 1-based
        else:
            chosen = 0
        answers.append(chosen)
        fill_scores.append(scores)
        # ambiguous if second best close to best
        sorted_idx = np.argsort(scores)[::-1]
        if len(scores) > 1:
            second = scores[sorted_idx[1]]
            if best_score - second < 0.08 and best_score >= threshold_fill*0.9:
                ambiguous.append({"question": q+1, "scores": scores})
        # draw circles in overlay
        for c in range(choices):
            cx, cy = int(centers[base + c][0]), int(centers[base + c][1])
            color = (0,255,0) if (c+1)==chosen and chosen!=0 else (0,0,255) if scores[c] >= threshold_fill else (180,180,180)
            cv2.circle(overlay, (cx,cy), 26, color, 2)
    return answers, fill_scores, overlay, ambiguous

def score_answers(answers, answer_key):
    per_subject = []
    total = 0
    # default: 5 subjects x 20 questions each
    # if answer_key length != 100, compute subject sizes heuristically: 5 equal parts
    n = len(answer_key)
    subjects = 5
    per_sub_count = n // subjects
    for s in range(subjects):
        start = s*per_sub_count
        end = start + per_sub_count
        correct = 0
        for i in range(start, end):
            det = answers[i]
            correct_opt = answer_key[i]
            if det !=0 and det == correct_opt:
                correct += 1
        per_subject.append(correct)
        total += correct
    return per_subject, total

def process_image(path, template_name="A", answer_key=None, save_overlay=True):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(path)
    rect = detect_sheet_corners(img)
    if rect is None:
        raise RuntimeError("sheet corners not found; try better photo or manual scan")
    warped, M = warp_to_canonical(img, rect)
    answers, scores, overlay, ambiguous = detect_answers_from_warp(warped, template_name)
    if answer_key is None:
        # load answer key from file if exists
        akp = Path("answer_keys.json")
        if akp.exists():
            with open(akp, "r") as f:
                keys = json.load(f)
            answer_key = keys.get(template_name)
    if answer_key is None:
        # fall back: zeros
        answer_key = [0]* (len(answers))
    per_sub, total = score_answers(answers, answer_key)
    # save overlay
    overlay_path = None
    if save_overlay:
        outp = Path("static") / "overlays"
        outp.mkdir(parents=True, exist_ok=True)
        outfn = Path(path).stem + "_overlay.png"
        overlay_path = str(outp / outfn)
        cv2.imwrite(overlay_path, overlay)
    result = {
        "per_subject": per_sub,
        "total": total,
        "answers": answers,
        "ambiguous": ambiguous,
        "overlay": overlay_path
    }
    return result

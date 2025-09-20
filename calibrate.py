# calibrate.py (manual corner selection)
import cv2, json
import numpy as np
from pathlib import Path
from omr_core import warp_to_canonical, CANON_W, CANON_H

# Hardcode image filename for simplicity
IMG_PATH = "sheet1.jpg"

img = cv2.imread(IMG_PATH)
if img is None:
    raise SystemExit(f"Image not found at {IMG_PATH}. Put your OMR sheet image in the same folder as calibrate.py.")

print("INSTRUCTIONS:")
print("1) A window will open with your OMR sheet.")
print("2) Click the 4 corners of the sheet in this order: TOP-LEFT, TOP-RIGHT, BOTTOM-RIGHT, BOTTOM-LEFT.")
print("3) After 4 clicks, press any key to continue.")

pts = []
def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append((x,y))
        cv2.circle(img, (x,y), 8, (0,0,255), -1)
        cv2.imshow("sheet", img)

cv2.imshow("sheet", img)
cv2.setMouseCallback("sheet", click)
cv2.waitKey(0)
cv2.destroyAllWindows()

if len(pts) != 4:
    raise SystemExit("You must click exactly 4 points (sheet corners).")

pts = np.array(pts, dtype="float32")
warped, _ = warp_to_canonical(cv2.imread(IMG_PATH), pts)
display = warped.copy()
pts_bubbles = []

def click_bubble(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pts_bubbles.append((x,y))
        cv2.circle(display, (x,y), 6, (0,0,255), -1)
        cv2.imshow("warped", display)

cv2.imshow("warped", display)
cv2.setMouseCallback("warped", click_bubble)

print("\nNEXT STEPS:")
print("1) Click TOP-LEFT bubble (A of Q1).")
print("2) Click the bubble to the RIGHT (B of Q1).")
print("3) Click the bubble BELOW the top-left (A of Q2).")
print("4) Click the TOP-LEFT bubble of column 2 (A of next section).")
print("Then press 's' to save template.")

while True:
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        cv2.destroyAllWindows()
        raise SystemExit("Cancelled")
    if k == ord('s'):
        if len(pts_bubbles) < 4:
            print("Need 4 bubble clicks, you have:", len(pts_bubbles))
            continue
        break

cv2.destroyAllWindows()

x0,y0 = pts_bubbles[0]
x_right,y_right = pts_bubbles[1]
x_down,y_down = pts_bubbles[2]
x_col2,y_col2 = pts_bubbles[3]

choice_dx = x_right - x0
q_dy = y_down - y0
col_dx = x_col2 - x0

total_q = int(input("Total number of questions (e.g. 100): ").strip())
choices = int(input("Choices per question (e.g. 4): ").strip())
num_columns = int(input("Number of columns (e.g. 5): ").strip())
per_col = total_q // num_columns

centers = []
for col in range(num_columns):
    base_x = x0 + col * col_dx
    for r in range(per_col):
        y = int(y0 + r * q_dy)
        for c in range(choices):
            x = int(base_x + c * choice_dx)
            centers.append([x,y])

template_name = input("Template name to save (e.g. A): ").strip()
out = {
    "template_name": template_name,
    "total_questions": total_q,
    "choices": choices,
    "num_columns": num_columns,
    "per_column": per_col,
    "choice_dx": choice_dx,
    "question_dy": q_dy,
    "column_dx": col_dx,
    "centers": centers
}
Path("templates").mkdir(parents=True, exist_ok=True)
with open(Path("templates") / f"{template_name}.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"✅ Template saved to templates/{template_name}.json")

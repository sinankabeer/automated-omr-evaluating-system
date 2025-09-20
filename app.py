# app.py - Streamlit OMR Evaluation with Excel Keys + ZIP Batch Support (Fixed Set A / Set B Mapping)
import streamlit as st
import cv2, numpy as np, pandas as pd, json, zipfile, re
from pathlib import Path
from omr_core import detect_sheet_corners, warp_to_canonical
import matplotlib.pyplot as plt

# --- CONFIG ---
TEMPLATE_PATH = Path("templates/A.json")   # Bubble positions template

# --- LOAD TEMPLATE ---
if not TEMPLATE_PATH.exists():
    st.error(f"Template not found: {TEMPLATE_PATH}")
    st.stop()

with open(TEMPLATE_PATH, "r") as f:
    template = json.load(f)

centers = template["centers"]
total_q = template["total_questions"]
choices = template["choices"]

subjects = ["Python", "EDA", "SQL", "Power BI", "Statistics"]

per_subject = total_q // len(subjects)

# --- HELPERS ---
def load_answer_keys_from_excel(file):
    """Convert Excel file with multiple sheets (Set A, Set B) to dictionary of answer keys"""
    mapping = {"A": 0, "B": 1, "C": 2, "D": 3}

    # Load all sheets
    df_dict = pd.read_excel(file, sheet_name=None)
    all_keys = {}

    for sheet_name, df in df_dict.items():
        numeric_answers = []

        # Process each column (skip Q.No if present)
        for col in df.columns:
            if str(col).strip().lower() in ["q.no", "question", "no"]:
                continue

            for x in df[col]:
                if pd.isna(x):
                    continue
                raw_value = str(x).strip().upper()

                # Cleanup formats like "21 - A", "81. A", "A,B"
                if "-" in raw_value:
                    raw_value = raw_value.split("-")[-1].strip()
                if "," in raw_value:
                    raw_value = raw_value.split(",")[0].strip()
                if "." in raw_value:
                    raw_value = raw_value.split(".")[-1].strip()

                if raw_value not in mapping:
                    continue
                numeric_answers.append(mapping[raw_value])

        # --- Explicit set mapping ---
        clean_name = sheet_name.strip().lower()
        if "a" in clean_name:
            set_name = "Set A"
        elif "b" in clean_name:
            set_name = "Set B"
        else:
            set_name = sheet_name  # fallback

        all_keys[set_name] = numeric_answers[:total_q]

        # Debug print in Streamlit
        st.sidebar.write(f"✅ Loaded {len(numeric_answers)} answers for {set_name} (from sheet {sheet_name})")

    return all_keys


def evaluate_sheet(img_bytes, answer_key, filename=None):
    """Evaluate a single OMR sheet image against selected answer_key"""
    img_np = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    if img is None:
        return None, None, None, filename

    rect = detect_sheet_corners(img)
    warped = img if rect is None else warp_to_canonical(img, rect)[0]
    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    answers, scores = [], {}
    for q in range(total_q):
        intensities = []
        for c in range(choices):
            x, y = centers[q * choices + c]
            x1, x2 = max(0, x-10), min(gray.shape[1], x+10)
            y1, y2 = max(0, y-10), min(gray.shape[0], y+10)
            roi = gray[y1:y2, x1:x2]
            val = 0 if roi.size == 0 else max(0, 255 - np.mean(roi))
            if val < 30:
                val = 0
            intensities.append(val)
        marked = int(np.argmax(intensities))
        answers.append(marked)

    # total score
    total_score = sum(1 for a, b in zip(answers, answer_key) if a == b)

    # per subject scores
    for i, subject in enumerate(subjects):
        start, end = i * per_subject, (i + 1) * per_subject
        scores[subject] = sum(1 for a, b in zip(answers[start:end], answer_key[start:end]) if a == b)

    # overlay visualization
    vis = warped.copy()
    for q in range(total_q):
        for c in range(choices):
            idx = q * choices + c
            if idx >= len(centers):
                continue
            x, y = centers[idx]
            color = (0, 255, 0) if answers[q] == c else (0, 0, 255)
            cv2.circle(vis, (x, y), 8, color, 2)
    vis_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)

    return total_score, scores, vis_rgb, filename


# --- STREAMLIT UI ---
st.title("📄 Automated OMR Evaluation System (Excel + ZIP Support)")

st.sidebar.header("🔑 Upload Answer Key")
key_file = st.sidebar.file_uploader("Upload Answer Key (Excel: xlsx)", type=["xlsx"])

if key_file:
    all_keys = load_answer_keys_from_excel(key_file)
    st.sidebar.success(f"Loaded Sets: {', '.join(all_keys.keys())}")

    mode = st.radio("Choose Mode:", ["Single Sheet", "Batch (ZIP)"])

    if mode == "Single Sheet":
        uploaded_file = st.file_uploader("Upload OMR Sheet", type=["jpg", "png", "jpeg"])
        version = st.selectbox("Select Exam Version", list(all_keys.keys()))
        if uploaded_file:
            answer_key = all_keys.get(version)
            score, scores, vis, _ = evaluate_sheet(uploaded_file.read(), answer_key, uploaded_file.name)
            if score is None:
                st.error("Could not process image")
            else:
                st.subheader(f"✅ Results (Version {version})")
                st.write(f"**Total Score: {score}/{total_q}**")
                for subj, val in scores.items():
                    st.write(f"{subj}: {val}/{per_subject}")
                st.image(vis, caption="Graded OMR Sheet", use_column_width=True)

    elif mode == "Batch (ZIP)":
        zip_file = st.file_uploader("Upload ZIP with Set A / Set B folders", type=["zip"])
        if zip_file:
            results, previews = [], []

            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                file_list = zip_ref.namelist()
                st.write(f"📂 Found {len(file_list)} files in ZIP")

                for file in file_list:
                    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
                        continue

                    fname_lower = file.lower()
                    if "set a" in fname_lower:
                        version = "Set A"
                    elif "set b" in fname_lower:
                        version = "Set B"
                    else:
                        continue

                    answer_key = all_keys.get(version)
                    if not answer_key or len(answer_key) != total_q:
                        st.write(f"⚠️ Skipping {file} (invalid/missing answer key for {version})")
                        continue

                    img_bytes = zip_ref.read(file)
                    score, scores, vis, student_name = evaluate_sheet(img_bytes, answer_key, Path(file).name)
                    if score is None:
                        continue

                    row = {"Student": student_name, "Set": version, "Total": score}
                    row.update(scores)
                    results.append(row)
                    previews.append((student_name, vis))

            if results:
                df = pd.DataFrame(results)
                st.subheader("📊 Batch Results")
                st.dataframe(df)

                st.subheader("🏆 Overall Leaderboard")
                st.bar_chart(df.set_index("Student")["Total"])

                st.subheader("📈 Subject-wise Averages")
                avg_scores = {subj: df[subj].mean() for subj in subjects}
                avg_df = pd.DataFrame(list(avg_scores.items()), columns=["Subject", "Average Score"])
                st.bar_chart(avg_df.set_index("Subject"))

                fig, ax = plt.subplots()
                ax.pie(avg_df["Average Score"], labels=avg_df["Subject"], autopct='%1.1f%%', startangle=90)
                ax.axis("equal")
                st.pyplot(fig)

                st.subheader("🎯 Top Scorers per Subject")
                for subj in subjects:
                    st.markdown(f"**{subj}**")
                    top_subj = df[["Student", subj]].sort_values(by=subj, ascending=False).head(3)
                    st.table(top_subj)

                st.subheader("🖼️ Graded Sheet Previews")
                for sid, vis in previews:
                    with st.expander(f"Preview - {sid}"):
                        st.image(vis, caption=f"Graded Overlay for {sid}", use_column_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download Results CSV", csv, "results.csv", "text/csv")
            else:
                st.error("❌ No valid results generated. Please check Set names and Answer Key.")
else:
    st.warning("⚠️ Please upload an Excel answer key (e.g., Key (Set A and B).xlsx) to begin.")

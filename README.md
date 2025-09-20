# Automated OMR Evaluation System

## 📌 Problem Statement
At Innomatics Research Labs, placement readiness assessments are conducted across roles like Data Analytics and AI/ML.  
Currently, OMR sheets (100 questions, 20 per subject across 5 subjects) are evaluated manually.  
This process is time-consuming, error-prone, and delays feedback for students.

## 🎯 Objective
- Accurately evaluate OMR sheets captured via mobile camera.
- Provide per-subject scores (20 each) and a total score (100).
- Support multiple exam sets (A, B, etc.).
- Run online via a web application.
- Maintain <0.5% error tolerance.
- Reduce evaluation turnaround from **days to minutes**.

## 💡 Solution
We built a **Scalable Automated OMR Evaluation System** with:
- Image preprocessing (rotation, skew, illumination correction).
- Bubble detection & evaluation (using OpenCV + NumPy).
- Multi-set answer key support (Excel upload).
- Per-subject & total scoring.
- Web application interface (Streamlit) with:
  - Single sheet & batch (ZIP) evaluation.
  - Leaderboards.
  - Subject-wise averages & visualizations.
  - Graded sheet previews.
- Results downloadable as CSV.

## 🧪 Subjects
Each OMR sheet has **100 questions**, grouped into 5 subjects:
- Python
- EDA
- SQL
- Power BI
- Statistics

Each subject contributes **20 questions (20 marks max)**.

## 🛠️ Tech Stack
- **Python** – Core programming
- **OpenCV** – Image processing
- **NumPy, Pandas** – Data manipulation
- **Matplotlib** – Charts & visualizations
- **Streamlit** – Web application
- **OpenPyXL** – Excel answer key handling

## ⚙️ Installation & Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/omr-evaluation.git
   cd omr-evaluation

python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

pip install -r requirements.txt

streamlit run app.py

📂 Usage

Upload Answer Key

Upload the provided Excel file (Key (Set A and B).xlsx) from the sidebar.

The app automatically parses and maps answers.

Single Sheet Mode

Upload a single .jpg/.jpeg/.png OMR sheet.

Select Set A or Set B.

View per-subject breakdown, total score, and graded preview.

Batch (ZIP) Mode

Upload a .zip file containing student OMR sheets inside Set A/ or Set B/ folders.

The app processes all sheets automatically.

Displays leaderboard, subject averages, pie chart distribution, and top scorers.

Download consolidated results as .csv.

## 📊 Sample Output

**Leaderboard**
https://github.com/sinankabeer/automated-omr-evaluating-system/blob/main/images/Overall%20leaderboard.png

**Subject-wise Averages**
https://github.com/sinankabeer/automated-omr-evaluating-system/blob/main/images/Subject%20wise%20averages.png

**Graded Sheet Preview**
https://github.com/sinankabeer/automated-omr-evaluating-system/blob/main/images/Graded%20sheet%20preview.png

**Pie chart**
https://github.com/sinankabeer/automated-omr-evaluating-system/blob/main/images/Pie%20chart.png

**Top score per subject**
https://github.com/sinankabeer/automated-omr-evaluating-system/blob/main/images/Top%20score%20per%20subject.png

**Download result CSV**
https://github.com/sinankabeer/automated-omr-evaluating-system/blob/main/images/Download%20Result%20CSV.png

## 🌐 Deployment

The project is deployed here:  
👉 [Streamlit App]https://automated-omr-evaluating-system-n5ejtwee77aes2zwetpgzm.streamlit.app/



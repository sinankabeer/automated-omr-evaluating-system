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

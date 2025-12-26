# 🛡️ Offline Smart ATS Resume Optimizer

A privacy-focused, offline Applicant Tracking System (ATS) optimizer built with Python. This tool uses **Natural Language Processing (NLP)** and **Vector Embeddings** to analyze resumes against job descriptions, providing a match score based on both *exact keywords* and *semantic meaning*.

> **Note:** Optimized for Apple Silicon (M1/M2/M3) chips but works on any standard Python environment.

---

## 🚀 Key Features

* **100% Offline & Private:** No data leaves your computer. Your resume and the JD are processed locally.
* **Dual Scoring System:**
    * **Keyword Match:** Identifies missing hard skills (e.g., "Python", "SQL").
    * **Semantic Match:** Uses AI (Vector Embeddings) to understand context (e.g., knowing that "Coding" is related to "Programming").
* **Smart Filtering:** Automatically filters out "fluff" words (e.g., "team player", "motivated") to focus on real technical skills.
* **File Support:** Handles both `.pdf` and `.docx` resume formats.
* **Automatic Setup:** Automatically downloads necessary AI models on the first run.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python-based UI)
* **NLP Processing:** [spaCy](https://spacy.io/)
* **Semantic Search:** [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
* **PDF/Doc Parsing:** `PyPDF2`, `python-docx`

---

## ⚙️ Installation Guide

### Prerequisites
* Python 3.10, 3.11, or 3.12 (Python 3.14 is currently not supported by some NLP libraries).
* *Recommended:* A virtual environment.

### 1. Clone the Repository

git clone https://github.com/Suraj317github/ats-resume-optimizer.git
cd ats-optimizer
2. Create a Virtual Environment

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

Windows:
python -m venv venv
.\venv\Scripts\activate


3. Install Dependencies
pip install streamlit spacy PyPDF2 python-docx sentence-transformers torch

Note for Mac M1/M2 Users: If you encounter issues, ensure you are using a native ARM64 Python installation (via Homebrew or Python.org) to leverage the Neural Engine speed.

🏃‍♂️ How to Run
Navigate to the project folder in your terminal.

Run the Streamlit app:
streamlit run app.py

The application will open automatically in your web browser (usually at http://localhost:8501).

First Run Note: The application will automatically download the required AI models (en_core_web_sm and all-MiniLM-L6-v2) upon the first launch. This may take 1-2 minutes depending on your internet connection.

🧠 How It Works
The application performs a 3-step analysis:

Text Extraction & Cleaning:

Extracts text from the uploaded PDF/DOCX.

Removes bullet points, special characters, and formatting noise.

Keyword Extraction (The "Hard" Skills):

Uses spaCy to identify Proper Nouns and Technical Nouns.

Filters out a custom list of "stop words" (generic office buzzwords).

Calculates an overlap percentage between JD and Resume.

Semantic Analysis (The "Soft" Meaning):

Uses Sentence-Transformers to convert the Resume and JD into high-dimensional vectors.

Calculates Cosine Similarity to determine how closely the documents match in meaning, even if the words are different.

The Scoring Formula
$$ \text{Final Score} = (\text{Keyword Score} \times 0.6) + (\text{Semantic Score} \times 0.4) $$

📂 Project Structure
ats-optimizer/
├── app.py                # Main application logic
├── README.md             # Project documentation
├── requirements.txt      # (Optional) List of dependencies
└── .gitignore            # Files to ignore (e.g., venv/)

🤝 Contributing
Contributions are welcome! If you have suggestions for improving the "fluff word" filter or optimizing the semantic model, feel free to fork the repo and submit a Pull Request.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

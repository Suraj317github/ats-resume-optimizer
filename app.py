import streamlit as st
import spacy
from collections import Counter
import PyPDF2
import docx
import re
import numpy as np
from sentence_transformers import SentenceTransformer, util

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart ATS Optimizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #ff4b4b, #feca57, #4CAF50);
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. AUTOMATIC MODEL LOADER ---
@st.cache_resource
def load_nlp_models():
    """
    Downloads and caches models automatically.
    This runs only once when you start the app.
    """
    # 1. Load Spacy (Grammar & Keywords)
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Auto-download if missing
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    # 2. Load Sentence Transformer (Semantic Meaning)
    # 'all-MiniLM-L6-v2' is fast (80MB) and perfect for offline use on Mac M2
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    return nlp, semantic_model

# Load models with a spinner so user knows what's happening
with st.spinner("Booting up AI Neural Networks (First run may take a minute)..."):
    nlp, semantic_model = load_nlp_models()

# --- 2. TEXT EXTRACTION ---
def read_file(uploaded_file):
    """Reads PDF or DOCX."""
    try:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        elif "wordprocessingml" in uploaded_file.type:
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception:
        return None

# --- 3. SMART CLEANING & PROCESSING ---
def clean_text(text):
    """Basic text cleaning."""
    text = re.sub(r'[•\*\-\|➢▪]', '', text) # Remove bullets
    text = re.sub(r'\s+', ' ', text).strip() # Remove extra spaces
    return text

def extract_keywords(text):
    """Extracts nouns/skills for Exact Match scoring."""
    doc = nlp(text.lower())
    keywords = set()
    ignored = {"team", "work", "skills", "experience", "role", "time", "services", "solutions", "environment"}
    
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2:
            if token.text not in ignored:
                keywords.add(token.text)
    return keywords

# --- 4. DUAL SCORING ALGORITHM ---
def calculate_scores(resume_text, jd_text):
    # A. Clean Texts
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)

    # B. Keyword Score (Exact Match)
    res_keys = extract_keywords(clean_resume)
    jd_keys = extract_keywords(clean_jd)
    
    match_count = len(res_keys.intersection(jd_keys))
    total_jd_keys = len(jd_keys)
    
    if total_jd_keys == 0:
        keyword_score = 0
    else:
        keyword_score = (match_count / total_jd_keys) * 100

    # C. Semantic Score (Context Match)
    # Convert entire text to vectors
    embedding_1 = semantic_model.encode(clean_resume, convert_to_tensor=True)
    embedding_2 = semantic_model.encode(clean_jd, convert_to_tensor=True)
    
    # Compute Cosine Similarity (Returns 0.0 to 1.0)
    similarity = util.cos_sim(embedding_1, embedding_2)
    semantic_score = similarity.item() * 100

    # D. Weighted Final Score
    # We give 60% weight to keywords (ATS are dumb) and 40% to semantic (Context)
    final_score = (keyword_score * 0.6) + (semantic_score * 0.4)
    
    return {
        "final": round(final_score, 1),
        "keyword": round(keyword_score, 1),
        "semantic": round(semantic_score, 1),
        "missing": jd_keys - res_keys,
        "matched": res_keys.intersection(jd_keys)
    }

# --- 5. MAIN GUI ---
def main():
    st.title("🧠 Smart ATS Analyzer (Semantic AI)")
    st.markdown("This tool uses **Vector Embeddings** to understand the *meaning* of your resume, not just the keywords.")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Job Description")
        jd_input = st.text_area("Paste JD here", height=250, label_visibility="collapsed")

    with col2:
        st.subheader("2. Resume")
        uploaded_file = st.file_uploader("Upload PDF/DOCX", type=["pdf", "docx"], label_visibility="collapsed")

    if st.button("Analyze Match", use_container_width=True):
        if jd_input and uploaded_file:
            with st.spinner("Calculating Semantic Vectors..."):
                resume_text = read_file(uploaded_file)
                
                if resume_text:
                    # RUN ANALYSIS
                    results = calculate_scores(resume_text, jd_input)
                    
                    # DISPLAY RESULTS
                    st.divider()
                    st.header(f"Overall Match: {results['final']}%")
                    st.progress(results['final'] / 100)
                    
                    # Metrics Row
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.info(f"**Exact Keyword Match**\n# {results['keyword']}%")
                        st.caption("How many specific words match exactly.")
                    with m2:
                        st.success(f"**Semantic Context**\n# {results['semantic']}%")
                        st.caption("How similar the 'meaning' of the text is.")
                    with m3:
                        st.warning(f"**Missing Terms**\n# {len(results['missing'])}")
                        st.caption("Keywords found in JD but not in Resume.")

                    # Missing Keywords Section
                    st.subheader("️ High Priority Missing Keywords")
                    st.write("Even if your semantic score is high, traditional ATS systems look for these exact words:")
                    
                    # Display tags
                    missing_list = sorted(list(results['missing']))
                    if missing_list:
                        st.markdown(
                            " ".join([f"<span style='background-color:#ffeeba; padding:5px; border-radius:5px; margin:2px; display:inline-block; color:black;'>{word}</span>" for word in missing_list]),
                            unsafe_allow_html=True
                        )
                    else:
                        st.write(" No critical keywords missing!")

        else:
            st.error("Please provide both a Job Description and a Resume file.")

if __name__ == "__main__":
    main()

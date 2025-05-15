# File: Home.py
import streamlit as st
import pandas as pd
from utils import (
    extract_text_from_pdf, extract_text_from_docx, chain, State
)

st.title("Resume Grader")

# File uploader
uploaded_file_job_desc = st.file_uploader(
    "Upload Job Description",
    type=["pdf", "docx"],
    accept_multiple_files=False
)
uploaded_file_qual = st.file_uploader(
    "Upload Qualifications",
    type=["pdf", "docx"],
    accept_multiple_files=False
)
uploaded_file_resumes = st.file_uploader(
    "Upload Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)
threshold = st.text_input("Enter Threshold Score")

if uploaded_file_job_desc:
    desc = extract_text_from_pdf(uploaded_file_job_desc) if uploaded_file_job_desc.name.endswith(".pdf") else extract_text_from_docx(uploaded_file_job_desc)
else:
    desc = ""

if uploaded_file_qual:
    qual = extract_text_from_pdf(uploaded_file_qual) if uploaded_file_qual.name.endswith(".pdf") else extract_text_from_docx(uploaded_file_qual)
else:
    qual = ""

if st.button("Submit"):
    st.success("Processing your input...")
    results = []
    if uploaded_file_resumes:
        for file in uploaded_file_resumes:
            st.subheader(f"Processing: {file.name}")
            resume = extract_text_from_pdf(file) if file.name.endswith(".pdf") else extract_text_from_docx(file)
            initial_state_input = State(
                resume_data=resume,
                job_desc=desc,
                qualifications=qual,
                resume_score=None,
                reason=None,
                skills=None,
                education=None,
                work_exp=None,
                projects=None,
                positives=None,
                negatives=None
            )
            config = {"configurable": {"thread_id": file.name}}
            for event in chain.stream(initial_state_input, config):
                if "Resume Grader" in event:
                    snapshot = chain.get_state(config)
                    result = snapshot[0]
                    result["filename"] = file.name
                    if int(result["resume_score"]) > int(threshold):
                        results.append(result)
        st.session_state["resume_results"] = results
        st.success("Scoring completed! Go to 'Resume Insights' page to view detailed reasons.")
        df = pd.DataFrame(results)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='scored_resumes.csv',
            mime='text/csv',
        )

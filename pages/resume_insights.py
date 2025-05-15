import streamlit as st

st.title("Resume Insights")

if "resume_results" in st.session_state:
    for result in st.session_state["resume_results"]:
        st.subheader(result["filename"])
        st.markdown(f"**Name:** {result['name']}")
        st.markdown(f"**Score:** {result['resume_score']}")
        st.markdown(f"**Positives:**\n\n{result['positives']}")
        st.markdown(f"**Negatives:**\n\n{result['negatives']}")
        st.markdown("---")
else:
    st.warning("No resume scores available. Please upload and evaluate resumes on the Home page.")

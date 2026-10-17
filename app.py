import json
from pathlib import Path

import streamlit as st
from src.tailor import tailor_resume

st.title("ResumeTailor")

profile = json.loads(
    Path("profile/master_resume.json").read_text()
)

job_offer = st.text_area(
    "Paste the job offer",
    height=300,
    placeholder="Paste the full job description here...",
)

if st.button("Tailor my resume", type="primary"):
    if not job_offer.strip():
        st.error("Paste a job description first.")
    else:
        with st.spinner("Analyzing the offer..."):
            result = tailor_resume(profile, job_offer)

        st.subheader("Proposed resume")
        st.write(result.professional_summary)

        st.subheader("Skills")
        st.write(", ".join(result.skills))

        st.subheader("Experience")
        for bullet in result.experience_bullets:
            st.write(f"- {bullet}")

        st.subheader("Requirements to review")
        st.write(result.missing_requirements)
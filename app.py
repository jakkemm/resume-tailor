import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.job_parser import extract_job_description
from src.tailor import build_tailored_pdf_schema
from src.pdf_parser import pdf_parser

WORKING_DIR = Path(__file__).resolve().parent
PROFILE_DIR = WORKING_DIR / "profiles"
DEFAULT_MODEL = "qwen2.5:3b"

st.set_page_config(
    page_title="Resume Builder",
    page_icon="🔨",
)


def list_profiles():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    files = [f for f in PROFILE_DIR.glob("*.json")]
    
    if len(files) == 0:
        st.error(f"No available profiles found in {PROFILE_DIR}. Go to Input Info app first and create profile.")
        return {}
    else:
        profiles = {}
        
        for f in files:
            parts = str(f.stem).split("_")
            name_handle = " ".join(p.capitalize() for p in parts[:-2])
            dt = parts[-2] + "_" + parts[-1]
            
            year_handle = datetime.strptime(dt, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            full_handle = f"{name_handle} {year_handle}"
            profiles[full_handle] = f
    
    return profiles

def load_profile(file):
    with file.open("r", encoding="utf-8") as f:
        profile = json.load(f)
    return profile

def get_job_desc():
    desc_type = st.radio(
        "Choose job offer input",
        ["Description", "URL"]
    )
    
    if desc_type == "Description":
        desc = st.text_area("Input job description")
    elif desc_type == "URL":
        url = st.text_input("Input url")
        desc = ""
        
        if st.button("Fetch description"):
            try:
                desc = extract_job_description(url)
            except Exception as exc:
                st.error(f"Error trying to fetch job description: \n{exc}")
        return desc


st.title("Resume Builder")

st.text("To build a resume, you need to create your profile. If you haven't done it yet, navigate to the sidebar and input your info.")

all_profiles_dict = list_profiles()
selected_profile = st.selectbox("Choose your profile", list(all_profiles_dict.keys()))

if selected_profile is not None:
    profile_file = all_profiles_dict[selected_profile]
    profile = load_profile(profile_file)
    st.json(profile, expanded=False)
    
    job_desc = get_job_desc()
    resume = build_tailored_pdf_schema(profile, job_desc, DEFAULT_MODEL)
    file = pdf_parser(resume, profile_file.name)
    
    st.pdf(file)

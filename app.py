import json
from datetime import datetime
from pathlib import Path

import streamlit as st

WORKING_DIR = Path(__file__).resolve().parent
PROFILE_DIR = WORKING_DIR / "profiles"

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


st.title("Resume Builder")

st.text("To build a resume, you need to create your profile. If you haven't done it yet, navigate to the sidebar and input your info.")

all_profiles_dict = list_profiles()
selected_profile = st.selectbox("Choose your profile", list(all_profiles_dict.keys()))
profile = load_profile(all_profiles_dict[selected_profile])
st.json(profile)

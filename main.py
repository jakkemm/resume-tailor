import streamlit as st

st.set_page_config(
    page_title="Resume Builder",
    page_icon="🔨",
    layout="wide",
)

resume_page = st.Page(
    "pages/resume_builder.py",
    title="Resume Builder",
    icon="🔨",
    default=True,
)

input_info_page = st.Page(
    "pages/input_info.py",
    title="Input Info",
    icon="📝",
)

page = st.navigation([resume_page, input_info_page])
page.run()
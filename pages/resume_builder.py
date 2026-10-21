import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.job_parser import extract_job_description
from src.pdf_parser import pdf_parser
from src.tailor import build_tailored_pdf_schema

WORKING_DIR = Path(__file__).resolve().parent
PROFILE_DIR = WORKING_DIR / "profiles"
DEFAULT_MODEL = "qwen2.5:3b"


st.set_page_config(
    page_title="Resume Builder",
    page_icon="🔨",
    layout="wide",
)


def profile_label(file: Path) -> str:
    """Create a readable label from a profile filename."""
    parts = file.stem.rsplit("_", 2)

    if len(parts) == 3:
        name, date_part, time_part = parts

        try:
            created_at = datetime.strptime(
                f"{date_part}_{time_part}",
                "%Y%m%d_%H%M%S",
            )
        except ValueError:
            pass
        else:
            name = name.replace("_", " ").title()
            return f"{name} · {created_at:%Y-%m-%d %H:%M:%S}"

    return file.stem.replace("_", " ").title()


def list_profiles() -> dict[str, Path]:
    """Return available profiles, newest first."""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(
        PROFILE_DIR.glob("*.json"),
        key=lambda file: file.stat().st_mtime,
        reverse=True,
    )

    return {
        profile_label(file): file
        for file in files
    }


def load_profile(file: Path) -> dict:
    """Load a profile from JSON."""
    with file.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_job_desc() -> str:
    """Collect a job description directly or by extracting it from a URL."""
    mode = st.radio(
        "Job offer input",
        ["Paste description", "Fetch from URL"],
        horizontal=True,
        key="job_input_mode",
    )

    if mode == "Paste description":
        return st.text_area(
            "Job description",
            placeholder="Paste the complete job description here...",
            height=250,
            key="job_description",
        )

    url = st.text_input(
        "Job offer URL",
        placeholder="https://example.com/jobs/...",
        key="job_url",
    )

    if st.button(
        "Fetch description",
        disabled=not url.strip(),
        key="fetch_description",
    ):
        try:
            with st.spinner("Extracting job description..."):
                description = extract_job_description(url.strip())

            if not description or not description.strip():
                raise ValueError("No job description could be extracted.")

            st.session_state["fetched_job_description"] = description.strip()
            st.success("Description extracted. Review it before generating.")

        except Exception as exc:
            st.session_state["fetched_job_description"] = ""
            st.error(f"Could not fetch the description: {exc}")

    return st.text_area(
        "Extracted description (editable)",
        height=250,
        key="fetched_job_description",
        placeholder="Fetch a description or paste one here...",
    )


def pdf_to_bytes(pdf_file) -> bytes:
    """Convert the PDF output into bytes suitable for downloading."""
    if isinstance(pdf_file, bytes):
        return pdf_file

    if isinstance(pdf_file, bytearray):
        return bytes(pdf_file)

    if isinstance(pdf_file, Path):
        return pdf_file.read_bytes()

    if isinstance(pdf_file, str):
        return Path(pdf_file).read_bytes()

    if hasattr(pdf_file, "getvalue"):
        return pdf_file.getvalue()

    raise TypeError(
        f"Unsupported PDF output type: {type(pdf_file).__name__}"
    )


# ---------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------

st.title("Resume Builder")
st.caption(
    "Tailor your resume to a job offer using your saved profile "
    "and a local language model."
)

profiles = list_profiles()

if not profiles:
    st.info(
        "No profiles found. Create a profile in the Input Info app "
        f"and save it to: `{PROFILE_DIR}`"
    )
    st.stop()


with st.container(border=True):
    st.subheader("1. Select your profile")

    selected_profile = st.selectbox(
        "Saved profiles",
        options=list(profiles),
    )

    profile_file = profiles[selected_profile]

    try:
        profile = load_profile(profile_file)
    except (OSError, json.JSONDecodeError) as exc:
        st.error(f"Could not load the profile: {exc}")
        st.stop()

    with st.expander("Review profile data"):
        st.json(profile)


with st.container(border=True):
    st.subheader("2. Add a job offer")

    job_desc = get_job_desc()

    st.caption(
        "Review the extracted text for missing sections before generating "
        "your resume."
    )

    generate = st.button(
        "Generate tailored resume",
        type="primary",
        disabled=not job_desc.strip(),
        use_container_width=True,
    )

    if generate:
        try:
            with st.spinner("Tailoring your resume and generating the PDF..."):
                resume_schema = build_tailored_pdf_schema(
                    profile,
                    job_desc,
                    DEFAULT_MODEL,
                )

                pdf_file = pdf_parser(resume_schema, profile_file.name)

                st.session_state["generated_resume"] = {
                    "profile_path": str(profile_file),
                    "job_description": job_desc,
                    "pdf_file": pdf_file,
                }

        except Exception as exc:
            st.error(f"Resume generation failed: {exc}")


# ---------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------

generated = st.session_state.get("generated_resume")

if generated and generated["profile_path"] == str(profile_file) and generated["job_description"] == job_desc:
    st.divider()
    st.subheader("3. Your tailored resume")

    try:
        pdf_bytes = pdf_to_bytes(generated["pdf_file"])

        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name=f"{profile_file.stem}_tailored.pdf",
            mime="application/pdf",
            type="primary",
        )
        st.pdf(
            pdf_bytes,
            height=850,
            key="resume_preview",
            alt="Preview of your tailored resume",
        )

    except (OSError, TypeError, ValueError) as exc:
        st.error(f"Could not display or download the PDF: {exc}")

elif generated:
    st.caption("Your inputs have changed since the previous generation. Generate again to update the preview.")

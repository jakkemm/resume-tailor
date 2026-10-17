import json

from ollama import chat
from pydantic import BaseModel


class TailoredResume(BaseModel):
    professional_summary: str
    skills: list[str]
    experience_bullets: list[str]
    selected_projects: list[str]
    missing_requirements: list[str]


def tailor_resume(profile: dict, job_offer: str) -> TailoredResume:
    response = chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": """
You are a careful resume editor.

Use only facts supported by the supplied candidate profile.
Never invent employers, dates, skills, responsibilities,
achievements, metrics, qualifications or project outcomes.

Tailor the resume to the job offer while preserving truth.
Prioritize relevant experience and use concise professional
language. Identify requirements the candidate cannot verify.
Return only the requested structured data.
""",
            },
            {
                "role": "user",
                "content": (
                    f"Candidate profile:\n"
                    f"{json.dumps(profile, ensure_ascii=False)}\n\n"
                    f"Job offer:\n{job_offer}"
                ),
            },
        ],
        format=TailoredResume.model_json_schema(),
        options={"temperature": 0.1, "num_ctx": 4096},
    )

    data = json.loads(response.message.content)
    return TailoredResume.model_validate(data)
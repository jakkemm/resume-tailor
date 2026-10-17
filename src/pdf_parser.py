import re
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

D = PROJECT_ROOT / "misc" / "Carlito"
pdfmetrics.registerFont(TTFont("C", D / "Carlito-Regular.ttf"))
pdfmetrics.registerFont(TTFont("C-B", D / "Carlito-Bold.ttf"))
pdfmetrics.registerFont(TTFont("C-I", D / "Carlito-Italic.ttf"))
pdfmetrics.registerFont(TTFont("C-BI", D / "Carlito-BoldItalic.ttf"))
pdfmetrics.registerFontFamily("C", normal="C", bold="C-B", italic="C-I", boldItalic="C-BI")

ACC = colors.HexColor("#1F4E79") 
GREY = colors.HexColor("#555555")
W, H = A4
M = 15 * mm
FS = 9.6

BODY = ParagraphStyle("b", fontName="C", fontSize=FS, leading=FS*1.28, textColor=colors.HexColor("#1a1a1a"))
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=10, bulletIndent=0, spaceAfter=1.6)
NAME = ParagraphStyle("n", fontName="C-B", fontSize=24, leading=27, textColor=ACC)
ROLE = ParagraphStyle("r", fontName="C", fontSize=12, leading=15, textColor=GREY)
CONTACT = ParagraphStyle("c", parent=BODY, fontSize=9.4, textColor=GREY, leading=12)
SEC = ParagraphStyle("s", fontName="C-B", fontSize=11, leading=13, textColor=ACC, spaceBefore=6, spaceAfter=1)
ROW_L = ParagraphStyle("rl", parent=BODY, fontName="C-B", fontSize=10.2)
ROW_R = ParagraphStyle("rr", parent=BODY, alignment=2, textColor=GREY)
SUB = ParagraphStyle("sub", parent=BODY, fontName="C-I", textColor=GREY, spaceAfter=1.5)

def S(text):
    return [
        Paragraph(escape(text.upper()), SEC),
        HRFlowable(width="100%", thickness=0.8, color=ACC, spaceAfter=3)
    ]
def B(text):
    return Paragraph(text, BUL, bulletText="•")
def row(left, right):
    table = Table(
        [[Paragraph(escape(str(left)), ROW_L), Paragraph(escape(str(right)), ROW_R)]],
        colWidths=[W - 2 * M - 45 * mm, 45 * mm]
    )

    table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table

def _parse_header(header):
    parts = [
        Paragraph(escape(header.name), NAME),
        Paragraph(escape("&nbsp;·&nbsp;".join(header.headline)), ROLE),
        Spacer(1, 2),
    ]

    contact = header.contact
    formatted = []

    fields = [
        ("location", contact.location),
        ("phone", contact.phone),
        ("email", contact.email),
        ("linkedin", contact.linkedin),
        ("github", contact.github),
    ]

    for field, value in fields:
        if not value:
            continue

        if field == "email":
            href = escape(f"mailto:{value}", {'"': "&quot;", "'": "&apos;"})
            formatted.append(f'<link href="{href}" color="#1F4E79">{escape(value)}</link>')
        elif field in ("linkedin", "github"):
            href = escape(value, {'"': "&quot;", "'": "&apos;"})
            formatted.append(f'<link href="{href}" color="#1F4E79">{escape(value)}</link>')
        else:
            formatted.append(escape(value))

    if formatted:
        contact_text = "&nbsp;·&nbsp;".join(formatted)
        parts.append(Paragraph(contact_text, CONTACT))

    return parts


def _parse_profile(profile: str) -> list:
    if not profile.strip():
        return []

    parts = S("Profile")
    parts.append(Paragraph(escape(profile), BODY))
    return parts

def _parse_bullet(bullet):
    text = bullet.bullet_text

    bolded = sorted({part for part in bullet.bolded_parts if part}, key=len, reverse=True)
    if not bolded:
        return B(escape(text))

    pattern = re.compile("|".join(re.escape(part) for part in bolded))

    chunks = []
    position = 0

    for match in pattern.finditer(text):
        chunks.append(escape(text[position:match.start()]))
        chunks.append(f"<b>{escape(match.group(0))}</b>")
        position = match.end()

    chunks.append(escape(text[position:]))
    return B("".join(chunks))

def _parse_professional_experience(items):
    if not items:
        return []

    parts = S("Professional Experience")

    for index, prof in enumerate(items):
        parts.append(row(f"{prof.job_title} — {prof.company_name}", prof.dates))

        if prof.context:
            parts.append(Paragraph(escape(prof.context), SUB))

        for bullet in prof.bullets:
            parts.append(_parse_bullet(bullet))

        if index < len(items) - 1:
            parts.append(Spacer(1, 2))

    return parts


def _parse_education(items):
    if not items:
        return []

    parts = S("Education")

    for index, edu in enumerate(items):
        parts.append(row(f"{edu.degree} — {edu.institution}", edu.dates))

        if edu.thesis:
            parts.append(Paragraph(f"Thesis: <i>{escape(edu.thesis)}</i>", BODY))

        if index < len(items) - 1:
            parts.append(Spacer(1, 2))

    return parts


def _parse_projects(items):
    if not items:
        return []

    parts = S("Selected Projects")

    for index, project in enumerate(items):
        parts.append(row(project.name, project.year))

        if project.technologies:
            technologies = " · ".join(project.technologies)
            parts.append(Paragraph(escape(technologies), SUB))

        for bullet in project.bullets:
            parts.append(_parse_bullet(bullet))

        if index < len(items) - 1:
            parts.append(Spacer(1, 2))

    return parts

def _format_skills(items):
    data = [
        [
            Paragraph(f"<b>{escape(skill.field)}</b>", BODY),
            Paragraph(escape(", ".join(skill.individual_skills)), BODY)
        ]
        for skill in items
    ]

    table = Table(data, colWidths=[36 * mm, W - 2 * M - 36 * mm])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.6),
    ]))
    return table


def _parse_skills(items):
    if not items:
        return []

    parts = S("Technical Skills")
    parts.append(_format_skills(items))
    return parts

def _parse_interests(interests):
    if not interests:
        return []

    parts = S("Areas of Interest")

    text = "&nbsp;·&nbsp;".join(
        escape(interest) for interest in interests
    )
    parts.append(Paragraph(text, BODY))

    return parts

def _build_consent_form(canvas, doc):
    canvas.setFont("C-I", 7)
    canvas.setFillColor(colors.HexColor("#999999"))
    canvas.drawCentredString(
        W / 2,
        5.5 * mm,
        "I consent to the processing of my personal data "
        "for the purposes of the recruitment process.",
    )


def pdf_parser(resume, profile_title):
    story = []

    story.extend(_parse_header(resume.header))
    story.extend(_parse_profile(resume.profile))
    story.extend(_parse_professional_experience(resume.professional_experience))
    story.extend(_parse_education(resume.education))
    story.extend(_parse_projects(resume.projects))
    story.extend(_parse_skills(resume.skills))
    story.extend(_parse_interests(resume.areas_of_interest))

    output_path = PROJECT_ROOT / "outputs" / f"{profile_title}.pdf"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=M,
        rightMargin=M,
        topMargin=12 * mm,
        bottomMargin=10 * mm,
    )

    doc.addPageTemplates([
        PageTemplate(
            id="p", 
            frames=[Frame(M, 10 * mm, W - 2 * M, H - 22 * mm, 0, 0, 0, 0)], 
            onPage=_build_consent_form
        )
    ])

    doc.build(story)

    # Basic output verification
    reader = PdfReader(str(output_path))
    if not reader.pages:
        raise RuntimeError("Generated PDF contains no pages.")

    return output_path
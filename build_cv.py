from pathlib import Path

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
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

D = Path.cwd() / "misc" / "Carlito"
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

body = ParagraphStyle("b", fontName="C", fontSize=FS, leading=FS*1.28, textColor=colors.HexColor("#1a1a1a"))
bul = ParagraphStyle("bul", parent=body, leftIndent=10, bulletIndent=0, spaceAfter=1.6)
name = ParagraphStyle("n", fontName="C-B", fontSize=24, leading=27, textColor=ACC)
role = ParagraphStyle("r", fontName="C", fontSize=12, leading=15, textColor=GREY)
contact = ParagraphStyle("c", parent=body, fontSize=9.4, textColor=GREY, leading=12)
sec = ParagraphStyle("s", fontName="C-B", fontSize=11, leading=13, textColor=ACC, spaceBefore=6, spaceAfter=1)
row_l = ParagraphStyle("rl", parent=body, fontName="C-B", fontSize=10.2)
row_r = ParagraphStyle("rr", parent=body, alignment=2, textColor=GREY)
sub = ParagraphStyle("sub", parent=body, fontName="C-I", textColor=GREY, spaceAfter=1.5)

def S(t): 
    return [Paragraph(t.upper(), sec), HRFlowable(width="100%", thickness=0.8, color=ACC, spaceAfter=3)]
def B(t): 
    return Paragraph(t, bul, bulletText="•")

def row(l,r):
    t = Table([[Paragraph(l,row_l),Paragraph(r,row_r)]],colWidths=[W-2*M-45*mm,45*mm])
    t.setStyle(
        TableStyle([
            ("LEFTPADDING",(0,0),(-1,-1),0),
            ("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0),
            ("BOTTOMPADDING",(0,0),(-1,-1),0.5)
        ])
    )
    return t

def skills(items):
    data = [[Paragraph(f"<b>{k}</b>", body), Paragraph(v, body)] for k, v in items]
    t = Table(data,colWidths=[36*mm, W-2*M-36*mm])
    t.setStyle(
        TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),0),
            ("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0.6),
            ("BOTTOMPADDING",(0,0),(-1,-1),0.6)])
    )
    return t

def header(role_text):
    s = [Paragraph("Jakub Kempa",name),Paragraph(role_text,role),Spacer(1,2)]
    s.append(Paragraph(
      'Wrocław, Poland &nbsp;|&nbsp; +48 796 978 706 &nbsp;|&nbsp; '
      '<link href="mailto:jak.kempa@gmail.com" color="#1F4E79">jak.kempa@gmail.com</link> &nbsp;|&nbsp; '
      '<link href="https://www.linkedin.com/in/jakub-kempa/" color="#1F4E79">linkedin.com/in/jakub-kempa</link> &nbsp;|&nbsp; '
      '<link href="https://github.com/jakkemm" color="#1F4E79">github.com/jakkemm</link>', contact))
    return s

def edu(thesis_line):
    return [row("MSc, Applied Mathematics — Wrocław University of Science and Technology","2025 – 2026"),
            Paragraph(thesis_line, body),
            Spacer(1,2),
            row("BEng, Applied Mathematics — Wrocław University of Science and Technology","2021 – 2025"),
            Paragraph("Thesis: <i>Time series models and machine learning approaches for traffic light optimization</i>.", body)]

ALPIQ_HDR = lambda: [
    row("Python Developer (Data &amp; Energy Markets) — Alpiq","06/2024 – 09/2026"),
    Paragraph("Energy trading &amp; analytics · European electricity-market data", sub)
]

story = []

# ============ PAGE 1: DATA ENGINEER ============
story += header("Data Engineer &nbsp;·&nbsp; Python &nbsp;·&nbsp; Data Pipelines")
story += S("Profile")
story.append(Paragraph(
    "Data Engineer with two years of commercial experience building Python data pipelines for the European "
    "electricity market, backed by a Master's degree in Applied Mathematics. Hands-on with API ingestion, "
    "SQL-heavy work on PostgreSQL, data-driven applications and team-based GitLab workflows. Comfortable with "
    "data at both extremes — high-frequency feeds refreshed every few minutes and very large numerical "
    "matrices. Looking for a hands-on engineering role in a team that builds real data systems.", body))

story += S("Professional Experience")
story += ALPIQ_HDR()
for t in [
    "Built and maintained <b>Python data loaders</b> ingesting and processing <b>millions of time-series records daily</b> from ~5 external APIs, managed via <b>Cron</b> with schedules ranging from weekly runs to continuous <b>5-minute refresh cycles</b>.",
    "Engineered end-to-end data flows (<b>API → Python/pandas → PostgreSQL → applications & ML models</b>), automating critical data delivery for downstream analytics.",
    "Wrote and optimized complex <b>SQL</b> on <b>PostgreSQL</b>; integrated <b>MongoDB</b> and <b>Redis</b> into the core data platform to support caching and unstructured storage.",
    "Maintained production environments across <b>AWS</b> and <b>Docker</b>, taking ownership of <b>GitLab CI/CD</b> deployments, failing run diagnostics, and Git code reviews.",
    "Refactored predictive models for <b>electricity price forecasting</b> to improve maintainability, and built internal <b>Streamlit</b> applications to visualize real-time model outputs.",
]: 
    story.append(B(t))

story += S("Technical Skills")
story.append(skills([
    ("Languages","Python (primary), SQL, Go (basic)"),
    ("Data Engineering","API integration, data ingestion, ETL workflows, data pipelines, scheduled &amp; near-real-time processing"),
    ("Databases","PostgreSQL (extensive), MongoDB, Redis"),
    ("Python Libraries","pandas, NumPy, SciPy, scikit-learn, statsmodels, pytest, Streamlit"),
    ("Infrastructure &amp; Tools","AWS, Docker, Git, GitLab, GitLab CI/CD, Linux, VS Code, Ruff, venv"),
    ("ML &amp; Analytics","Time-series forecasting (SARIMAX, Prophet), Random Forest, XGBoost, regression, PCA, genetic algorithms, cross-validation"),
]))

story += S("Selected Projects")
story.append(Spacer(1,3))
story.append(row("Statistical Denoising of fMRI Data — MSc Thesis","2026"))
story.append(Paragraph("Python · NumPy · SciPy · real-world dataset: OpenNeuro ds000105 (Visual Object Recognition)", sub))
for t in [
    "Processed very large numerical datasets (<b>~164,000 spatial locations × ~1,450 time points</b>), using <b>chunked computation</b> to keep memory use and runtime manageable.",
    "Designed a modular, object-oriented code base, supporting repeatable experiments and method comparison.",
]: 
    story.append(B(t))
    
story.append(row("Traffic Light Optimization with Forecasting &amp; Genetic Algorithms — BEng Thesis", "2025"))
story.append(Paragraph("Python · pandas · scikit-learn · XGBoost · Prophet · statsmodels · SciPy · PyGAD", sub))
for t in [
    "Built automated <b>Python ETL pipelines</b> to collect, clean and impute <b>real urban traffic sensor data</b>, using cubic spline interpolation and statistical noise augmentation.",
    "Trained and benchmarked forecasting models (<b>SARIMAX, Prophet, Random Forest, XGBoost</b>) with cross-validation to predict directional traffic volumes.",
    "Applied <b>genetic algorithms (PyGAD)</b> on the forecasts to optimise signal-light cycles, minimising congestion and waiting times.",
]: 
    story.append(B(t))


story += S("Education")
story += edu("Thesis: <i>Selected statistical methods in fMRI image denoising</i>.")
story += S("Areas of Interest")
story.append(Paragraph("MLOps &nbsp;·&nbsp; Data Science &nbsp;·&nbsp; Data infrastructure &nbsp;·&nbsp; Cloud &amp; AI security &nbsp;·&nbsp; Backend data systems", body))
story.append(PageBreak())






# ============ PAGE 2: DATA SCIENTIST ============
story += header("Data Scientist &nbsp;·&nbsp; Machine Learning &nbsp;·&nbsp; Statistical Modelling")
story += S("Profile")
story.append(Paragraph(
    "Data Scientist with an MSc in Applied Mathematics and a strong foundation in statistics, linear algebra and "
    "numerical methods, combined with two years of commercial experience in Python-based forecasting for the "
    "European electricity market. Implemented statistical and dimensionality-reduction methods (GLM, FGLS, PCA, ICA) "
    "on very large real-world datasets. Brings a practical mindset: models that run reliably beyond the notebook.", body))

story += S("Professional Experience")
story += ALPIQ_HDR()
for t in [
    "Enhanced and refactored core <b>electricity price forecasting models</b> on European energy data, improving code maintainability, validation setup, and model reliability for downstream trading decisions.",
    "Engineered Python/pandas <b>feature pipelines and input flows</b> ingesting ~5 data sources (ranging from daily to 5-minute refresh cycles) backed by <b>PostgreSQL</b> to power real-time model inference.",
    "Built interactive <b>Streamlit dashboards</b> to visualize price forecasts, model performance, and feature outputs for internal energy traders and analysts.",
    "Collaborated in a team environment using <b>Git/GitLab</b> (CI/CD pipelines, MR code reviews), containerizing workflows with <b>Docker</b> on <b>AWS</b> cloud infrastructure.",
]:
    story.append(B(t))

story += S("Education")
story += edu("Thesis: <i>Selected statistical methods in fMRI image denoising</i>.")

story += S("Selected Projects")
story.append(row("Statistical Denoising of fMRI Data — MSc Thesis", "2026"))
story.append(Paragraph("Python · NumPy · SciPy · real-world dataset: OpenNeuro ds000105 (Visual Object Recognition) · Nilearn",sub))
for t in [
    "Applied and compared denoising methods for fMRI/BOLD data: <b>GLM</b> (design matrix, HRF, nuisance regressors, high-pass filtering), <b>FGLS</b> with <b>AR(1)</b> autocorrelation modelling and <b>prewhitening</b>, <b>PCA</b> and <b>ICA</b>.",
    "Worked with high-dimensional data (<b>~164,000 spatial locations × ~1,450 time points</b>); estimated per-run AR(1) parameters, analysed explained variance and component selection via <b>SVD / eigenvalue analysis</b>.",
    "Used ICA to identify noise components and evaluated how each method affected signal quality across the experiments.",
    "Implemented everything end-to-end: preprocessing, methods, experiments and result analysis, using chunked estimation to handle the data volume. Structured as reusable classes (shared FGLS/prewhitening layer, separate PCA and ICA modules).",
]: 
    story.append(B(t))

story.append(Spacer(1,3))
story.append(row("Traffic Light Optimization — BEng Thesis", "2025"))
story.append(Paragraph("Python · pandas · scikit-learn · XGBoost · Prophet · statsmodels · SciPy · PyGAD", sub))
for t in [
    "Trained and benchmarked forecasting models (<b>SARIMAX, Facebook Prophet, Random Forest, XGBoost</b>) with <b>cross-validation</b> to predict directional traffic volumes from real urban sensor data.",
    "Built automated <b>Python ETL pipelines</b> to collect, clean and impute the data (cubic spline interpolation, statistical noise augmentation).",
    "Applied <b>genetic algorithms (PyGAD)</b> on the predicted time series to optimise signal-light cycles, directly minimising congestion and waiting times.",
]: 
    story.append(B(t))

story += S("Technical Skills")
story.append(skills([
    ("Statistics &amp; Maths","Regression, GLM, FGLS, time-series analysis (AR models), probability, linear algebra, numerical methods, optimisation, multivariate analysis"),
    ("ML &amp; Modelling","Time-series forecasting (SARIMAX, Prophet), Random Forest, XGBoost, genetic algorithms, PCA, ICA, SVD, cross-validation, model selection"),
    ("Python Stack","pandas, NumPy, SciPy, scikit-learn, statsmodels, XGBoost, Prophet, PyGAD, Streamlit"),
    ("Data &amp; Tools","SQL (PostgreSQL), MongoDB, Redis, Git, GitLab, Docker, AWS, Linux, LaTeX, VS Code"),
    ("Languages","Python (primary), SQL, Go (basic)"),
]))

story += S("Areas of Interest")
story.append(Paragraph("Machine Learning &nbsp;·&nbsp; MLOps &nbsp;·&nbsp; Data infrastructure &nbsp;·&nbsp; Time-series forecasting &nbsp;·&nbsp; AI security", body))

def pn(c, d):
    c.setTitle("Jakub Kempa — CV")
    c.setAuthor("Jakub Kempa")
    c.setFont("C-I", 7)
    c.setFillColor(colors.HexColor("#999999"))
    c.drawCentredString(W/2, 5.5*mm, "I consent to the processing of my personal data for the purposes of the recruitment process.")

output = str(Path.cwd() / "Jakub_Kempa_CV.pdf")
doc = BaseDocTemplate(output, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=12*mm, bottomMargin=10*mm)
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(M, 10*mm, W-2*M, H-22*mm, 0, 0, 0, 0)], onPage=pn)])
doc.build(story)

print(len(PdfReader(output).pages))

# utils/export.py
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def export_text_to_pdf(text, filename="notes.pdf"):
    styles = getSampleStyleSheet()
    story = []
    for para in text.split("\n\n"):
        story.append(Paragraph(para.replace("\n","<br/>"), styles['Normal']))
        story.append(Spacer(1, 8))
    doc = SimpleDocTemplate(filename, pagesize=A4)
    doc.build(story)
    return filename

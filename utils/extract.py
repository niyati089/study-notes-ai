# utils/extract.py
import pypdf
import base64

def extract_pdf(file_obj):
    """Accepts an uploaded file-like object and returns extracted text."""
    reader = pypdf.PdfReader(file_obj)
    text = []
    for page in reader.pages:
        ptext = page.extract_text()
        if ptext:
            text.append(ptext)
    return "\n".join(text)

def display_pdf(file_obj):
    """Return an HTML iframe for Streamlit display. file_obj is the uploaded BytesIO."""
    file_obj.seek(0)
    base64_pdf = base64.b64encode(file_obj.read()).decode('utf-8')
    return f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px"></iframe>'

from pypdf import PdfReader
import os

def extract_text_from_pdf(file_path: str) -> str:
    """
    The 'Optical Nerve': Opens a PDF and extracts every word.
    """
    if not os.path.exists(file_path):
        return "Error: PDF file not found."
        
    try:
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                full_text += content + "\n"
        return full_text.strip()
    except Exception as e:
        return f"PDF Extraction Error: {str(e)}"
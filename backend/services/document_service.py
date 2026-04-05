from pypdf import PdfReader
import os
from docx import Document
import mimetypes

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file.
    Handles both text-based and image-based PDFs.
    """
    if not os.path.exists(file_path):
        return "Error: PDF file not found."
        
    try:
        reader = PdfReader(file_path)
        
        if len(reader.pages) == 0:
            return "Error: PDF is empty (no pages found)."
        
        full_text = ""
        pages_with_text = 0
        
        for page_num, page in enumerate(reader.pages):
            try:
                content = page.extract_text()
                if content and content.strip():
                    full_text += content + "\n"
                    pages_with_text += 1
            except Exception as page_error:
                print(f"  Warning: Could not extract text from page {page_num + 1}: {str(page_error)}")
                continue
        
        if not full_text.strip():
            return "Error: PDF contains no extractable text. It may be a scanned image-based PDF or encrypted. Please convert to text-based PDF or use OCR."
        
        print(f"  ✓ Extracted text from {pages_with_text}/{len(reader.pages)} pages")
        return full_text.strip()
        
    except Exception as e:
        error_msg = str(e)
        if "encrypted" in error_msg.lower():
            return f"Error: PDF is encrypted. Please remove the password protection and try again."
        elif "corrupted" in error_msg.lower():
            return f"Error: PDF appears to be corrupted and cannot be read."
        else:
            return f"PDF Extraction Error: {error_msg}"

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from Word document.
    """
    if not os.path.exists(file_path):
        return "Error: DOCX file not found."
        
    try:
        doc = Document(file_path)
        full_text = ""
        for paragraph in doc.paragraphs:
            full_text += paragraph.text + "\n"
        return full_text.strip()
    except Exception as e:
        return f"DOCX Extraction Error: {str(e)}"

def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from plain text file.
    """
    if not os.path.exists(file_path):
        return "Error: TXT file not found."
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        return f"TXT Extraction Error: {str(e)}"

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from file based on its extension.
    Supports: PDF, DOCX, TXT
    """
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        return f"Unsupported file type: {ext}. Supported: PDF, DOCX, TXT"
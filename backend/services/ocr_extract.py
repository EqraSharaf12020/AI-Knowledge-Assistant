"""
Optional OCR support for scanned/image-based PDFs.

Install with: pip install pdf2image pytesseract pillow
Also requires Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki

Usage:
    from services.ocr_extract import extract_text_from_pdf_with_ocr
    text = extract_text_from_pdf_with_ocr("path/to/scanned.pdf")
"""

try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

def extract_text_from_pdf_with_ocr(file_path: str) -> str:
    """
    Extract text from scanned/image-based PDFs using OCR.
    
    Requirements:
    - pip install pdf2image pytesseract pillow
    - Tesseract OCR installed on system
    
    Returns: Extracted text or error message
    """
    if not HAS_OCR:
        return "Error: OCR dependencies not installed. Run: pip install pdf2image pytesseract pillow"
    
    try:
        import os
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        
        print(f"  Converting PDF to images (this may take a minute)...")
        images = convert_from_path(file_path, dpi=150)
        
        full_text = ""
        for page_num, image in enumerate(images, 1):
            print(f"    Processing page {page_num}/{len(images)}...")
            text = pytesseract.image_to_string(image)
            if text.strip():
                full_text += text + "\n"
        
        if not full_text.strip():
            return "Error: OCR could not extract any text from PDF."
        
        print(f"  ✓ OCR extracted {len(full_text)} characters from {len(images)} pages")
        return full_text.strip()
        
    except Exception as e:
        return f"OCR Error: {str(e)}"

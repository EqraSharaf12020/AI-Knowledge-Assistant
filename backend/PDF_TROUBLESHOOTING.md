# PDF Extraction Troubleshooting Guide

## Common Errors and Solutions

### Error: "PDF contains no extractable text. It may be a scanned image-based PDF"

**Cause**: Your PDF is a scanned document (image-based) or has text only in image form.

**Solutions**:
1. **Use Online OCR** (Recommended for single files)
   - Upload to [ILovePDF.com](https://www.ilovepdf.com/ocr) or [smallpdf.com](https://smallpdf.com/ocr-pdf)
   - Download the text-extractable PDF
   - Add to training folder and run `python train.py` again

2. **Install Local OCR** (For batch processing)
   ```bash
   # Install Python OCR packages
   pip install pdf2image pytesseract pillow
   
   # Install Tesseract OCR on your system:
   # Windows: https://github.com/UB-Mannheim/tesseract/wiki
   # Mac: brew install tesseract
   # Linux: sudo apt-get install tesseract-ocr
   ```
   
   Then use in code:
   ```python
   from services.ocr_extract import extract_text_from_pdf_with_ocr
   text = extract_text_from_pdf_with_ocr("your_scanned.pdf")
   ```

### Error: "PDF is encrypted"

**Cause**: PDF is password-protected.

**Solutions**:
1. Open PDF in your PDF reader
2. Try exporting/saving as a new PDF without password protection
3. Use online tools like [PDFUnlock](https://www.pdfunlock.com/)

### Error: "PDF appears to be corrupted"

**Cause**: PDF file is damaged or incomplete.

**Solutions**:
1. Try opening the PDF in multiple PDF readers to confirm it's readable
2. Use online repair tools like [Repair PDF Online](https://www.repair-pdf.com/)
3. Re-download the file if it was corrupted during transfer

### Empty Results

**Cause**: PDF has pages but no readable text.

**Solutions**:
1. Verify the PDF is truly text-based (try copying text in PDF reader)
2. Try a different PDF reader to ensure compatibility
3. Check file size is reasonable (< 100 MB for best results)

## File Size Impact

- **Small PDFs** (< 5 MB): Fastest extraction, no issues
- **Medium PDFs** (5-50 MB): Normal processing time
- **Large PDFs** (> 50 MB): May cause memory issues during training
  - **Solution**: Split into smaller PDFs before training

## Supported Formats

✅ **Fully Supported**:
- Text-based PDFs (can copy text in PDF reader)
- DOCX (Word documents)
- TXT (Plain text files)

⚠️ **Partially Supported** (requires OCR):
- Scanned PDFs / Image-based PDFs
- PDFs generated from images

❌ **Not Supported**:
- Password-protected/encrypted PDFs (need to unlock first)
- Corrupted PDFs (need to repair first)
- Binary/proprietary formats

## Testing Your PDF

To verify a PDF is text-extractable:

```python
from services.document_service import extract_text_from_pdf

text = extract_text_from_pdf("your_file.pdf")
print(f"Extracted {len(text)} characters")
print(text[:200])  # Print first 200 characters
```

If you get a proper text output, the PDF is ready for training.

## Batch Processing Recommendations

1. **Start small**: Test with 1-2 small PDFs first
2. **Verify quality**: Check extracted text makes sense
3. **Scale up**: Add more PDFs once confident
4. **Monitor memory**: Watch system resources during training with large documents

## Need More Help?

If your PDF still fails:
1. Try extracting just that file using `extract_text_from_pdf()` to see exact error
2. Open the PDF in a text editor or online viewer to check if it's readable
3. Consider converting using free tools like [ILovePDF](https://www.ilovepdf.com/)

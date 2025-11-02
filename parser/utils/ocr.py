"""
OCR fallback utility for extracting text from PDFs when pdfplumber fails.
"""

import pdfplumber
import pytesseract


def extract_text_with_ocr_fallback(pdf_path):
    """
    Extract text from PDF using pdfplumber, with OCR fallback if needed.
    
    First attempts to extract text using pdfplumber. If the extracted text
    is empty or too short, falls back to OCR using pytesseract.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        str: Extracted text from PDF
    """
    # First try: pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join([
                page.extract_text() or "" 
                for page in pdf.pages
            ])
        
        # If we got meaningful text (more than just whitespace), return it
        if text and len(text.strip()) > 50:
            return text
    except Exception as e:
        print(f"Warning: pdfplumber extraction failed: {e}")
    
    # Fallback: OCR using pytesseract
    print(f"Falling back to OCR for {pdf_path}...")
    try:
        ocr_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    # Convert page to image
                    pil_image = page.to_image(resolution=300).original
                    
                    # Perform OCR
                    page_text = pytesseract.image_to_string(pil_image)
                    ocr_text.append(page_text)
                except Exception as e:
                    print(f"Warning: OCR failed for page {page_num + 1}: {e}")
                    continue
        
        combined_text = "\n".join(ocr_text)
        return combined_text if combined_text else ""
        
    except Exception as e:
        print(f"Error: OCR fallback failed: {e}")
        return ""


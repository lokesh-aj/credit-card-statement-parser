"""
Parser for OneCard credit card statements.
"""

import re
from parser.utils.ocr import extract_text_with_ocr_fallback
from parser.utils.normalize import (
    normalize_currency,
    normalize_date,
    extract_card_last4,
    calculate_confidence
)


def extract_dates(text):
    """
    Extract billing period dates from text.
    
    Looks for patterns like: "14 Aug 2025 - 13 Sep 2025" or similar formats.
    
    Args:
        text: Text to search in
        
    Returns:
        tuple: (start_date_str, end_date_str) or (None, None)
    """
    # Pattern 1: (14 Aug 2025 - 13 Sep 2025) or similar
    match = re.search(r"(\d{1,2}\s+\w+\s+\d{4})\s*[-–]\s*(\d{1,2}\s+\w+\s+\d{4})", text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    
    # Pattern 2: DD/MM/YYYY - DD/MM/YYYY
    match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*[-–]\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    
    return None, None


def parse_onecard(path):
    """
    Parse OneCard credit card statement PDF.
    
    Extracts:
    - Card last 4 digits
    - Billing period (start and end)
    - Payment due date
    - Minimum amount due
    - New balance / Total amount due
    - Confidence score
    
    Args:
        path: Path to PDF file
        
    Returns:
        dict: Extracted data with confidence score
    """
    try:
        # Extract text with OCR fallback
        text = extract_text_with_ocr_fallback(path)
        
        if not text or len(text.strip()) < 10:
            return {
                "issuer": "OneCard",
                "card_last4": None,
                "billing_period": {"start": None, "end": None},
                "payment_due_date": None,
                "minimum_due": None,
                "new_balance": None,
                "confidence": 0.0
            }
        
        # Extract card last 4 digits (avoiding false positives)
        last4 = extract_card_last4(text, ['Card', 'Account', 'OneCard'])
        if not last4:
            # Fallback: look for last 4 digits near "OneCard" or card-related text
            match = re.search(r"(?:OneCard|Card)\s*(?:Number|No\.?)[:\s]+.*?(\d{4})\b", text, re.IGNORECASE)
            if match:
                last4 = match.group(1)
        
        # Extract billing period
        start, end = extract_dates(text)
        start_normalized = normalize_date(start) if start else None
        end_normalized = normalize_date(end) if end else None
        
        # Extract payment due date
        due_match = re.search(r"Payment\s+Due\s+Date[:\s]+([\w\d\s/\-]+)", text, re.IGNORECASE)
        due_date = None
        if due_match:
            due_date = normalize_date(due_match.group(1).strip())
        
        # Extract minimum amount due
        mindue_match = re.search(r"Minimum\s+Amount\s+Due[:\s]+([₹$]?[\d,\.\s]+)", text, re.IGNORECASE)
        mindue = None
        if mindue_match:
            mindue = normalize_currency(mindue_match.group(1))
        
        # Extract new balance / total amount due
        newbal_match = re.search(r"(?:New\s+Balance|Total\s+Amount\s+Due)[:\s]+([₹$]?[\d,\.\s]+)", text, re.IGNORECASE)
        newbal = None
        if newbal_match:
            newbal = normalize_currency(newbal_match.group(1))
        
        # Build result dictionary
        result = {
            "issuer": "OneCard",
            "card_last4": last4,
            "billing_period": {
                "start": start_normalized,
                "end": end_normalized
            },
            "payment_due_date": due_date,
            "minimum_due": mindue,
            "new_balance": newbal,
            "confidence": 0.0  # Will be calculated below
        }
        
        # Calculate confidence score
        result["confidence"] = calculate_confidence(result)
        
        return result
        
    except Exception as e:
        print(f"Error parsing OneCard statement: {e}")
        return {
            "issuer": "OneCard",
            "card_last4": None,
            "billing_period": {"start": None, "end": None},
            "payment_due_date": None,
            "minimum_due": None,
            "new_balance": None,
            "confidence": 0.0
        }

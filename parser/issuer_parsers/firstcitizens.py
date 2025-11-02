"""
Parser for FirstCitizens credit card statements.
"""

import re
from parser.utils.ocr import extract_text_with_ocr_fallback
from parser.utils.normalize import (
    normalize_currency,
    normalize_date,
    extract_card_last4,
    calculate_confidence
)


def parse_firstcitizens(path):
    """
    Parse FirstCitizens credit card statement PDF.
    
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
                "issuer": "FirstCitizens",
                "card_last4": None,
                "billing_period": {"start": None, "end": None},
                "payment_due_date": None,
                "minimum_due": None,
                "new_balance": None,
                "confidence": 0.0
            }
        
        # Extract card last 4 digits
        last4 = extract_card_last4(text, ['Account', 'Card', 'Number', 'FirstCitizens'])
        if not last4:
            # Fallback: look for "Account Number: ...XXXX"
            match = re.search(r"Account\s+Number[:\s]+(?:.*?[X*\s-]+)?(\d{4})\b", text, re.IGNORECASE)
            if match:
                last4_candidate = match.group(1)
                # Verify it's not a year
                if not (1900 <= int(last4_candidate) <= 2099):
                    last4 = last4_candidate
        
        # Extract billing period
        cycle_match = re.search(r"(?:Billing\s+Cycle|Statement\s+Period)[:\s]+([\w\d\s/]+)\s*[-–]\s*([\w\d\s/]+)", text, re.IGNORECASE)
        start_normalized = None
        end_normalized = None
        if cycle_match:
            start_normalized = normalize_date(cycle_match.group(1).strip())
            end_normalized = normalize_date(cycle_match.group(2).strip())
        
        # Extract payment due date
        due_match = re.search(r"(?:Payment\s+Due\s+Date|Due\s+Date)[:\s]+([\w\d\s/\-]+)", text, re.IGNORECASE)
        due_date = None
        if due_match:
            due_date = normalize_date(due_match.group(1).strip())
        
        # Extract minimum payment / minimum due
        mindue_match = re.search(r"(?:Minimum\s+Payment|Minimum\s+Due)[:\s]+([₹$]?[\d,\.\s]+)", text, re.IGNORECASE)
        mindue = None
        if mindue_match:
            mindue = normalize_currency(mindue_match.group(1))
        
        # Extract new balance / total amount due
        newbal_match = re.search(r"(?:New\s+Balance|Total\s+Amount\s+Due|Amount\s+Due)[:\s]+([₹$]?[\d,\.\s]+)", text, re.IGNORECASE)
        newbal = None
        if newbal_match:
            newbal = normalize_currency(newbal_match.group(1))
        
        # Build result dictionary
        result = {
            "issuer": "FirstCitizens",
            "card_last4": last4,
            "billing_period": {
                "start": start_normalized,
                "end": end_normalized
            },
            "payment_due_date": due_date,
            "minimum_due": mindue,
            "new_balance": newbal,
            "confidence": 0.0
        }
        
        # Calculate confidence score
        result["confidence"] = calculate_confidence(result)
        
        return result
        
    except Exception as e:
        print(f"Error parsing FirstCitizens statement: {e}")
        return {
            "issuer": "FirstCitizens",
            "card_last4": None,
            "billing_period": {"start": None, "end": None},
            "payment_due_date": None,
            "minimum_due": None,
            "new_balance": None,
            "confidence": 0.0
        }

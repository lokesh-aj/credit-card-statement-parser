"""
Parser for BuildingBlocks credit card statements.
"""

import re
from parser.utils.ocr import extract_text_with_ocr_fallback
from parser.utils.normalize import (
    normalize_currency,
    normalize_date,
    extract_card_last4,
    calculate_confidence
)


def parse_buildingblocks(path):
    """
    Parse BuildingBlocks credit card statement PDF.
    
    Extracts:
    - Card last 4 digits
    - Billing period (start and end)
    - Payment due date
    - Minimum amount due
    - New balance
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
                "issuer": "BuildingBlocks",
                "card_last4": None,
                "billing_period": {"start": None, "end": None},
                "payment_due_date": None,
                "minimum_due": None,
                "new_balance": None,
                "confidence": 0.0
            }
        
        # Extract card last 4 digits
        last4 = extract_card_last4(text, ['Account', 'Card', 'Number'])
        if not last4:
            # Fallback: look for "Account Number: ...XXXX"
            match = re.search(r"Account\s+Number[:\s]+(?:.*?[X*\s-]+)?(\d{4})\b", text, re.IGNORECASE)
            if match:
                last4 = match.group(1)
        
        # Extract billing period (Opening/Closing Date)
        cycle_match = re.search(r"Opening[/\s]+Closing\s+Date[:\s]+([\d/\-\s]+)\s*[-–]\s*([\d/\-\s]+)", text, re.IGNORECASE)
        start_normalized = None
        end_normalized = None
        if cycle_match:
            start_normalized = normalize_date(cycle_match.group(1).strip())
            end_normalized = normalize_date(cycle_match.group(2).strip())
        else:
            # Alternative pattern
            alt_match = re.search(r"(?:Billing\s+Period|Statement\s+Period)[:\s]+([\d/\-\s]+)\s*[-–]\s*([\d/\-\s]+)", text, re.IGNORECASE)
            if alt_match:
                start_normalized = normalize_date(alt_match.group(1).strip())
                end_normalized = normalize_date(alt_match.group(2).strip())
        
        # Extract payment due date
        due_match = re.search(r"Payment\s+Due\s+Date[:\s]+([\d/\-\w\s]+)", text, re.IGNORECASE)
        due_date = None
        if due_match:
            due_date = normalize_date(due_match.group(1).strip())
        
        # Extract minimum payment
        mindue_match = re.search(r"Minimum\s+Payment[:\s]+([$₹]?[\d,\.\s]+)", text, re.IGNORECASE)
        mindue = None
        if mindue_match:
            mindue = normalize_currency(mindue_match.group(1))
        
        # Extract new balance
        newbal_match = re.search(r"New\s+Balance[:\s]+([$₹]?[\d,\.\s]+)", text, re.IGNORECASE)
        newbal = None
        if newbal_match:
            newbal = normalize_currency(newbal_match.group(1))
        else:
            # Fallback: Total Amount Due
            fallback_match = re.search(r"Total\s+Amount\s+Due[:\s]+([$₹]?[\d,\.\s]+)", text, re.IGNORECASE)
            if fallback_match:
                newbal = normalize_currency(fallback_match.group(1))
        
        # Build result dictionary
        result = {
            "issuer": "BuildingBlocks",
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
        print(f"Error parsing BuildingBlocks statement: {e}")
        return {
            "issuer": "BuildingBlocks",
            "card_last4": None,
            "billing_period": {"start": None, "end": None},
            "payment_due_date": None,
            "minimum_due": None,
            "new_balance": None,
            "confidence": 0.0
        }

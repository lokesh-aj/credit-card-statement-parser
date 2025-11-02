"""
Utility functions for normalizing currency values and dates.
"""

import re
from dateutil import parser as date_parser
from datetime import datetime


def normalize_currency(value):
    """
    Normalize currency string to float.
    
    Removes currency symbols (₹, $, etc.), commas, and whitespace,
    then converts to float. Returns None if conversion fails.
    
    Args:
        value: String or numeric value to normalize
        
    Returns:
        float or None: Normalized currency value, or None if invalid
    """
    if value is None:
        return None
    
    try:
        # Convert to string if not already
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[₹$€£,\s]', '', str(value))
        
        # Handle empty strings
        if not cleaned:
            return None
        
        # Convert to float
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def normalize_date(date_str):
    """
    Normalize date string to YYYY-MM-DD format using python-dateutil.
    
    Handles various date formats and returns ISO format string.
    Returns None if parsing fails.
    
    Args:
        date_str: String representation of date in any format
        
    Returns:
        str or None: Date in YYYY-MM-DD format, or None if invalid
    """
    if date_str is None:
        return None
    
    try:
        # Strip whitespace
        date_str = str(date_str).strip()
        
        if not date_str:
            return None
        
        # Parse using dateutil
        parsed_date = date_parser.parse(date_str, dayfirst=True, yearfirst=False)
        
        # Return in ISO format
        return parsed_date.strftime('%Y-%m-%d')
    except (ValueError, TypeError, AttributeError):
        return None


def extract_card_last4(text, context_keywords=None):
    """
    Extract card last 4 digits from text, avoiding false positives like years.
    
    Looks for card numbers with context keywords to avoid matching years or other 4-digit numbers.
    More robust than simple regex patterns.
    
    Args:
        text: Text to search in
        context_keywords: List of keywords that should appear near the card number
                         (e.g., ['Card', 'Account', 'XXXX', 'Ending'])
        
    Returns:
        str or None: Last 4 digits of card, or None if not found
    """
    if not text:
        return None
    
    # Default context keywords
    if context_keywords is None:
        context_keywords = ['Card', 'Account', 'XXXX', 'Ending', 'Number']
    
    # Pattern 1: XXXX XXXX XXXX 1234 or similar masked format
    masked_pattern = r'(?:XXXX|[*•]{4}|[\d]{4})\s*(?:[-*\s]*)\s*(?:XXXX|[*•]{4}|[\d]{4})\s*(?:[-*\s]*)\s*(?:XXXX|[*•]{4}|[\d]{4})\s*(?:[-*\s]*)\s*(\d{4})'
    match = re.search(masked_pattern, text, re.IGNORECASE)
    if match:
        last4 = match.group(1)
        try:
            year_val = int(last4)
            # Verify it's not a year (1900-2099)
            if not (1900 <= year_val <= 2099):
                return last4
        except ValueError:
            return last4
    
    # Pattern 2: Card Ending in 1234 or Card Number: ...1234
    for keyword in context_keywords:
        pattern = rf'{keyword}[:\s]+(?:.*?)?(\d{{4}})(?!\d)'
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            # Get the last match (most likely to be the card number)
            for match in reversed(matches):
                last4 = match.group(1)
                try:
                    # Exclude years (1900-2099) and common 4-digit codes
                    year_val = int(last4)
                    if not (1900 <= year_val <= 2099):
                        # Check if it's near other card-related keywords
                        start = max(0, match.start() - 50)
                        end = min(len(text), match.end() + 50)
                        context = text[start:end]
                        if any(kw.lower() in context.lower() for kw in ['card', 'account', 'number', 'ending', 'xxxx']):
                            return last4
                except ValueError:
                    # Not a valid integer, skip
                    continue
    
    # Pattern 3: Standalone 4 digits at end of account number lines
    # Look for lines that contain account/card info
    lines = text.split('\n')
    for line in lines:
        if any(kw.lower() in line.lower() for kw in ['account', 'card', 'number']):
            # Find 4-digit number in this line
            match = re.search(r'(\d{4})(?!\d)', line)
            if match:
                last4 = match.group(1)
                try:
                    year_val = int(last4)
                    if not (1900 <= year_val <= 2099):
                        return last4
                except ValueError:
                    # Not a valid integer, skip
                    continue
    
    return None


def calculate_confidence(data):
    """
    Calculate overall confidence score based on extracted fields.
    
    Each field contributes to the confidence score. Fields that are None reduce confidence.
    
    Args:
        data: Dictionary with extracted fields
        
    Returns:
        float: Confidence score between 0.0 and 1.0
    """
    required_fields = [
        'card_last4',
        'billing_period',
        'payment_due_date',
        'new_balance'
    ]
    
    optional_fields = ['minimum_due']
    
    score = 0.0
    max_score = len(required_fields) + (len(optional_fields) * 0.5)
    
    # Check required fields
    for field in required_fields:
        if field == 'billing_period':
            if data.get(field) and isinstance(data[field], dict):
                if data[field].get('start') and data[field].get('end'):
                    score += 1.0
        else:
            if data.get(field) is not None:
                score += 1.0
    
    # Check optional fields
    if data.get('minimum_due') is not None:
        score += 0.5
    
    return round(score / max_score, 2) if max_score > 0 else 0.0


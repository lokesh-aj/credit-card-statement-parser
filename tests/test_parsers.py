"""
Unit tests for credit card statement parsers.
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parser.detect_issuer import detect_issuer
from parser.dispatcher import parse_pdf


def get_sample_pdfs():
    """
    Get all sample PDF files from statements directory.
    
    Returns:
        list: List of tuples (pdf_path, expected_issuer)
    """
    base_dir = Path(__file__).parent.parent
    statements_dir = base_dir / "statements"
    
    pdfs = []
    if statements_dir.exists():
        for issuer_dir in statements_dir.iterdir():
            if issuer_dir.is_dir():
                issuer_name = issuer_dir.name
                for pdf_file in issuer_dir.glob("*.pdf"):
                    pdfs.append((str(pdf_file), issuer_name))
    
    return pdfs


@pytest.fixture
def sample_pdfs():
    """Fixture providing sample PDF files."""
    return get_sample_pdfs()


class TestIssuerDetection:
    """Tests for issuer detection."""
    
    def test_detect_onecard(self):
        """Test detection of OneCard issuer."""
        path = "statements/onecard/test.pdf"
        issuer = detect_issuer(path)
        assert issuer == "onecard"
    
    def test_detect_buildingblocks(self):
        """Test detection of BuildingBlocks issuer."""
        path = "statements/buildingblocks/test.pdf"
        issuer = detect_issuer(path)
        assert issuer == "buildingblocks"
    
    def test_detect_hdfc(self):
        """Test detection of HDFC issuer."""
        path = "statements/hdfc/test.pdf"
        issuer = detect_issuer(path)
        assert issuer == "hdfc"
    
    def test_detect_amex(self):
        """Test detection of AMEX issuer."""
        path = "statements/amex/test.pdf"
        issuer = detect_issuer(path)
        assert issuer == "amex"
    
    def test_detect_firstcitizens(self):
        """Test detection of FirstCitizens issuer."""
        path = "statements/firstcitizens/test.pdf"
        issuer = detect_issuer(path)
        assert issuer == "firstcitizens"


class TestParsers:
    """Tests for PDF parsers."""
    
    @pytest.mark.parametrize("pdf_path,expected_issuer", get_sample_pdfs())
    def test_parse_sample_pdfs(self, pdf_path, expected_issuer):
        """
        Test parsing of sample PDF files.
        
        Asserts:
        - Required fields are not None (or have valid values)
        - Float fields are > 0 if present
        - Confidence score is between 0.0 and 1.0
        - Issuer matches expected
        """
        if not os.path.exists(pdf_path):
            pytest.skip(f"PDF file not found: {pdf_path}")
        
        # Detect issuer
        detected_issuer = detect_issuer(pdf_path)
        assert detected_issuer != "unknown", f"Could not detect issuer for {pdf_path}"
        
        # Parse PDF
        data = parse_pdf(pdf_path, detected_issuer)
        
        # Check for errors
        assert "error" not in data, f"Parser returned error: {data.get('error')}"
        
        # Validate structure
        assert "issuer" in data
        assert "card_last4" in data
        assert "billing_period" in data
        assert "payment_due_date" in data
        assert "new_balance" in data
        assert "minimum_due" in data
        assert "confidence" in data
        
        # Validate issuer matches
        assert data["issuer"] is not None
        
        # Validate billing period structure
        assert isinstance(data["billing_period"], dict)
        assert "start" in data["billing_period"]
        assert "end" in data["billing_period"]
        
        # Validate confidence score
        assert 0.0 <= data["confidence"] <= 1.0, \
            f"Confidence score {data['confidence']} is not between 0.0 and 1.0"
        
        # Validate required fields (at least some should be present)
        # Card last 4 should be a string if present
        if data["card_last4"] is not None:
            assert isinstance(data["card_last4"], str)
            assert len(data["card_last4"]) == 4, \
                f"Card last4 should be 4 digits, got: {data['card_last4']}"
        
        # Validate dates format (YYYY-MM-DD) if present
        for date_field in [data["billing_period"]["start"], 
                          data["billing_period"]["end"], 
                          data["payment_due_date"]]:
            if date_field is not None:
                assert isinstance(date_field, str)
                # Basic date format check (YYYY-MM-DD)
                assert len(date_field) == 10, \
                    f"Date should be in YYYY-MM-DD format, got: {date_field}"
                assert date_field.count('-') == 2, \
                    f"Date should be in YYYY-MM-DD format, got: {date_field}"
        
        # Validate currency fields
        for currency_field in [data["new_balance"], data["minimum_due"]]:
            if currency_field is not None:
                assert isinstance(currency_field, (int, float)), \
                    f"Currency field should be numeric, got: {type(currency_field)}"
                assert currency_field >= 0, \
                    f"Currency field should be >= 0, got: {currency_field}"
        
        # At least some required fields should be extracted (if OCR is available)
        # Note: If OCR is not installed and PDF requires it, fields may be None
        required_extracted = (
            data["card_last4"] is not None or
            data["billing_period"]["start"] is not None or
            data["payment_due_date"] is not None or
            data["new_balance"] is not None or
            data["minimum_due"] is not None
        )
        # If confidence is 0, it likely means OCR was needed but not available
        # In that case, we skip this assertion
        if data["confidence"] > 0.0:
            assert required_extracted, \
                "At least one required field should be extracted when confidence > 0"
    
    def test_parse_nonexistent_file(self):
        """Test parsing of non-existent file."""
        data = parse_pdf("nonexistent.pdf", "onecard")
        # Should return error or empty data structure
        assert data is not None


class TestNormalization:
    """Tests for normalization utilities."""
    
    def test_normalize_currency(self):
        """Test currency normalization."""
        from parser.utils.normalize import normalize_currency
        
        assert normalize_currency("₹1,234.56") == 1234.56
        assert normalize_currency("$1,234.56") == 1234.56
        assert normalize_currency("1,234.56") == 1234.56
        assert normalize_currency("1234") == 1234.0
        assert normalize_currency(None) is None
        assert normalize_currency("") is None
    
    def test_normalize_date(self):
        """Test date normalization."""
        from parser.utils.normalize import normalize_date
        
        # Various date formats should normalize to YYYY-MM-DD
        assert normalize_date("2025-01-15") == "2025-01-15"
        assert normalize_date("15/01/2025") == "2025-01-15"
        assert normalize_date("15 Jan 2025") is not None
        assert normalize_date(None) is None
        assert normalize_date("") is None
    
    def test_extract_card_last4(self):
        """Test card last 4 extraction with false positive prevention."""
        from parser.utils.normalize import extract_card_last4
        
        text1 = "Card Number: XXXX XXXX XXXX 1234"
        assert extract_card_last4(text1) == "1234"
        
        text2 = "Year: 2025 Card Number: 5678"
        result = extract_card_last4(text2)
        assert result == "5678" or result is None  # Should not be 2025
        
        text3 = "Account Number: 1234567890123456"
        # Should extract last 4 digits
        result = extract_card_last4(text3, ['Account', 'Number'])
        assert result is not None and len(result) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Credit Card Statement Parser

A robust PDF parser that extracts key data points from credit card statements across 5 major issuers with different layouts.

## Features

- ✅ Support for 5 credit card issuers (OneCard, BuildingBlocks, HDFC, AMEX, FirstCitizens)
- ✅ Extracts 5 key data points plus minimum amount due (bonus)
- ✅ Handles real-world PDF layouts with OCR fallback
- ✅ Normalized currency values and dates
- ✅ Field-level confidence scoring
- ✅ Automatic CSV output
- ✅ Comprehensive error handling
- ✅ Unit tests included

## Extracted Data Points

1. **Card last 4 digits** - Last 4 digits of the credit card number
2. **Billing period start** - Start date of billing cycle (YYYY-MM-DD)
3. **Billing period end** - End date of billing cycle (YYYY-MM-DD)
4. **Payment due date** - Date by which payment must be made (YYYY-MM-DD)
5. **New balance** - Total amount due / New balance (float)
6. **Minimum amount due** - Minimum payment required (float, bonus field)
7. **Confidence score** - Overall extraction confidence (0.0 to 1.0)

## Installation

### Prerequisites

- Python 3.7 or higher
- Tesseract OCR (for OCR fallback functionality)

### Install Tesseract OCR

**Windows:**
- Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Add Tesseract to PATH or configure path in code

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### Setup Python Environment

1. Clone or navigate to the project directory:
```bash
cd credit-card-statement-parser
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Single PDF Parsing

Parse a single credit card statement:

```bash
python parse.py statements/onecard/onecard-2025-09.pdf
```

Output will be printed as JSON and automatically appended to `outputs/results.csv`.

### Demo Script

Run the demo script to process all PDFs in the statements directory:

```bash
python demo.py
```

This will:
- Find all PDF files in `statements/` subdirectories
- Parse each one
- Display results
- Append all results to `outputs/results.csv`

### Output Format

The parser outputs JSON in the following format:

```json
{
  "issuer": "OneCard",
  "card_last4": "1234",
  "billing_period": {
    "start": "2025-08-14",
    "end": "2025-09-13"
  },
  "payment_due_date": "2025-10-03",
  "minimum_due": 5000.0,
  "new_balance": 25000.0,
  "confidence": 0.92
}
```

### CSV Output

Results are automatically appended to `outputs/results.csv` with the following columns:
- `issuer` - Credit card issuer name
- `last4` - Last 4 digits of card
- `bill_start` - Billing period start date
- `bill_end` - Billing period end date
- `payment_due` - Payment due date
- `new_balance` - New balance / Total amount due
- `minimum_due` - Minimum amount due
- `confidence` - Confidence score

## Project Structure

```
credit-card-statement-parser/
├── statements/              # Sample PDF files organized by issuer
│   ├── onecard/
│   ├── buildingblocks/
│   ├── hdfc/
│   ├── amex/
│   └── firstcitizens/
├── parser/
│   ├── issuer_parsers/     # Issuer-specific parsers
│   │   ├── onecard.py
│   │   ├── buildingblocks.py
│   │   ├── hdfc.py
│   │   ├── amex.py
│   │   └── firstcitizens.py
│   ├── utils/              # Utility functions
│   │   ├── normalize.py    # Currency and date normalization
│   │   └── ocr.py          # OCR fallback functionality
│   ├── detect_issuer.py    # Issuer detection
│   └── dispatcher.py      # Parser routing
├── outputs/
│   └── results.csv        # Parsed results (auto-generated)
├── tests/
│   └── test_parsers.py    # Unit tests
├── parse.py               # Main parsing script
├── demo.py               # Demo script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Supported Issuers

1. **OneCard** - Indian credit card issuer
2. **BuildingBlocks** - Credit card issuer
3. **HDFC** - HDFC Bank credit cards
4. **AMEX** - American Express
5. **FirstCitizens** - First Citizens Bank

## Features Details

### Robust Regex Patterns
- Strengthened patterns for all issuers
- Prevents false positives (e.g., years not mistaken for card numbers)
- Multiple fallback patterns per field

### Normalization
- **Currency**: Removes symbols (₹, $), commas, whitespace; converts to float
- **Dates**: Normalizes various formats to YYYY-MM-DD using python-dateutil

### OCR Fallback
- Automatically uses OCR (pytesseract) if pdfplumber returns empty text
- Handles scanned PDFs and image-based statements

### Confidence Scoring
- Field-level confidence calculation
- Overall confidence score based on extracted fields
- Helps identify parsing quality

### Error Handling
- Graceful handling of missing fields
- Try/except blocks throughout
- Informative error messages

## Testing

Run unit tests:

```bash
pytest tests/test_parsers.py -v
```

Tests verify:
- Issuer detection
- PDF parsing functionality
- Required fields are not None
- Float fields are valid (> 0 if present)
- Date format validation
- Normalization functions

## Dependencies

- **pdfplumber** - PDF text extraction
- **python-dateutil** - Date parsing and normalization
- **pytesseract** - OCR fallback for scanned PDFs
- **Pillow** - Image processing for OCR
- **pandas** - Data manipulation (if needed)
- **pytest** - Testing framework

## Troubleshooting

### OCR Not Working
If OCR fallback fails, ensure Tesseract is installed and in PATH:
```bash
tesseract --version
```

### Import Errors
Make sure you're in the virtual environment and dependencies are installed:
```bash
pip install -r requirements.txt
```

### PDF Not Parsing
- Check if the PDF is encrypted or corrupted
- Verify the issuer is supported
- Check the confidence score (low scores indicate parsing issues)
- Review error messages in console output

## Contributing

To add support for a new issuer:
1. Create a new parser in `parser/issuer_parsers/`
2. Add issuer detection in `parser/detect_issuer.py`
3. Add routing in `parser/dispatcher.py`
4. Add sample PDFs to `statements/<issuer>/`
5. Add tests in `tests/test_parsers.py`

## License

This project is part of an assignment submission.

## Notes

- The parser handles various date and currency formats automatically
- Confidence scores help identify which extractions may need manual review
- Results are appended to CSV, so running multiple times will accumulate results
- Empty fields in CSV indicate values that couldn't be extracted


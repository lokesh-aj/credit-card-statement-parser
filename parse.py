"""
Main script for parsing credit card statements.
Handles PDF parsing, issuer detection, and CSV output.
"""

import sys
import csv
import json
import os
from parser.detect_issuer import detect_issuer
from parser.dispatcher import parse_pdf


def append_to_csv(data, csv_path="outputs/results.csv"):
    """
    Append parsing results to CSV file.
    
    Creates the file with headers if it doesn't exist, then appends a new row.
    
    Args:
        data: Dictionary with extracted data
        csv_path: Path to CSV file
    """
    try:
        # Ensure outputs directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        # Check if file exists and has headers
        file_exists = os.path.isfile(csv_path)
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'issuer', 'last4', 'bill_start', 'bill_end',
                'payment_due', 'new_balance', 'minimum_due', 'confidence'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Prepare row data
            row = {
                'issuer': data.get('issuer', ''),
                'last4': data.get('card_last4', ''),
                'bill_start': data.get('billing_period', {}).get('start', '') if isinstance(data.get('billing_period'), dict) else '',
                'bill_end': data.get('billing_period', {}).get('end', '') if isinstance(data.get('billing_period'), dict) else '',
                'payment_due': data.get('payment_due_date', ''),
                'new_balance': data.get('new_balance', ''),
                'minimum_due': data.get('minimum_due', ''),
                'confidence': data.get('confidence', 0.0)
            }
            
            writer.writerow(row)
            
    except Exception as e:
        print(f"Warning: Failed to append to CSV: {e}")


def main():
    """
    Main entry point for the parser.
    
    Accepts PDF path as command line argument, parses it, prints JSON output,
    and appends results to CSV file.
    """
    if len(sys.argv) < 2:
        print("Usage: python parse.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    
    # Validate PDF file exists
    if not os.path.isfile(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    try:
        # Detect issuer
        issuer = detect_issuer(pdf_path)
        if issuer == "unknown":
            print(f"Warning: Could not detect issuer for {pdf_path}")
        
        # Parse PDF
        data = parse_pdf(pdf_path, issuer)
        
        # Check for parsing errors
        if "error" in data:
            print(f"Error: {data['error']}")
            sys.exit(1)
        
        # Print JSON output (as required)
        print(json.dumps(data, indent=2))
        
        # Append to CSV
        append_to_csv(data)
        
    except Exception as e:
        print(f"Error: Failed to parse PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

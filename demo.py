"""
Demo script to parse all credit card statements in the statements directory.
Loops through all PDF files and displays results.
"""

import os
import json
from pathlib import Path
from parser.detect_issuer import detect_issuer
from parser.dispatcher import parse_pdf


def find_all_pdfs(base_dir="statements"):
    """
    Find all PDF files in the statements directory.
    
    Args:
        base_dir: Base directory containing issuer subdirectories
        
    Returns:
        list: List of (pdf_path, issuer) tuples
    """
    pdfs = []
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Error: Directory '{base_dir}' not found")
        return pdfs
    
    # Iterate through issuer directories
    for issuer_dir in sorted(base_path.iterdir()):
        if issuer_dir.is_dir():
            issuer_name = issuer_dir.name
            # Find all PDF files in this directory
            for pdf_file in sorted(issuer_dir.glob("*.pdf")):
                pdfs.append((str(pdf_file), issuer_name))
    
    return pdfs


def main():
    """Main demo function."""
    print("=" * 80)
    print("Credit Card Statement Parser - Demo")
    print("=" * 80)
    print()
    
    # Find all PDFs
    pdfs = find_all_pdfs()
    
    if not pdfs:
        print("No PDF files found in statements directory.")
        print("Please add PDF files to the appropriate issuer subdirectories.")
        return
    
    print(f"Found {len(pdfs)} PDF file(s) to process.\n")
    
    # Process each PDF
    results = []
    for idx, (pdf_path, expected_issuer) in enumerate(pdfs, 1):
        print(f"[{idx}/{len(pdfs)}] Processing: {os.path.basename(pdf_path)}")
        print(f"  Expected issuer: {expected_issuer}")
        
        try:
            # Detect issuer
            detected_issuer = detect_issuer(pdf_path)
            print(f"  Detected issuer: {detected_issuer}")
            
            # Parse PDF
            data = parse_pdf(pdf_path, detected_issuer)
            
            # Check for errors
            if "error" in data:
                print(f"  [ERROR] Error: {data['error']}")
                results.append({
                    "file": pdf_path,
                    "status": "error",
                    "error": data["error"]
                })
                print()
                continue
            
            # Display extracted data
            print(f"  [OK] Parsed successfully")
            print(f"  Card Last 4: {data.get('card_last4', 'N/A')}")
            print(f"  Billing Period: {data.get('billing_period', {}).get('start', 'N/A')} to {data.get('billing_period', {}).get('end', 'N/A')}")
            print(f"  Payment Due Date: {data.get('payment_due_date', 'N/A')}")
            print(f"  New Balance: {data.get('new_balance', 'N/A')}")
            print(f"  Minimum Due: {data.get('minimum_due', 'N/A')}")
            print(f"  Confidence: {data.get('confidence', 0.0):.2%}")
            
            results.append({
                "file": pdf_path,
                "status": "success",
                "data": data
            })
            
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            results.append({
                "file": pdf_path,
                "status": "error",
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    
    print(f"Total processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        avg_confidence = sum(
            r["data"].get("confidence", 0.0) 
            for r in results 
            if r["status"] == "success"
        ) / successful
        print(f"Average confidence: {avg_confidence:.2%}")
    
    print()
    print("Results have been appended to outputs/results.csv")
    print("=" * 80)


if __name__ == "__main__":
    main()


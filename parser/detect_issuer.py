def detect_issuer(pdf_path):
    if "onecard" in pdf_path.lower():
        return "onecard"
    if "buildingblocks" in pdf_path.lower():
        return "buildingblocks"
    if "hdfc" in pdf_path.lower():
        return "hdfc"
    if "amex" in pdf_path.lower():
        return "amex"
    if "firstcitizens" in pdf_path.lower():
        return "firstcitizens"
    return "unknown"

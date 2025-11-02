from parser.issuer_parsers.onecard import parse_onecard
from parser.issuer_parsers.buildingblocks import parse_buildingblocks
from parser.issuer_parsers.hdfc import parse_hdfc
from parser.issuer_parsers.amex import parse_amex
from parser.issuer_parsers.firstcitizens import parse_firstcitizens

def parse_pdf(path, issuer):
    if issuer == "onecard":
        return parse_onecard(path)
    if issuer == "buildingblocks":
        return parse_buildingblocks(path)
    if issuer == "hdfc":
        return parse_hdfc(path)
    if issuer == "amex":
        return parse_amex(path)
    if issuer == "firstcitizens":
        return parse_firstcitizens(path)
    return {"error": "issuer not supported"}

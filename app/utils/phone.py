"""
Phone number validation and normalization utilities
"""
import phonenumbers
from phonenumbers import NumberParseException
import re

def normalize_phone_number(phone: str, default_region: str = "IR") -> str:

#def normalize_phone_number(phone: str, default_region: str = "AE") -> str:
    """
    Normalize phone number to E.164 format
    
    Args:
        phone: Phone number in any format
        default_region: Default country code if not provided (default: AE for UAE)
    
    Returns:
        Phone number in E.164 format (e.g., +971501234567)
    """
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    try:
        # Parse the phone number
        parsed = phonenumbers.parse(cleaned, default_region)
        
        # Format to E.164
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        
    except NumberParseException:
        # If parsing fails, return cleaned version with + if not present
        if not cleaned.startswith('+'):
            return '+' + cleaned
        return cleaned


def validate_phone_number(phone: str, default_region: str = "IR") -> bool:
    """
    Validate if phone number is valid
    
    Args:
        phone: Phone number to validate
        default_region: Default country code if not provided
    
    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = phonenumbers.parse(phone, default_region)
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False

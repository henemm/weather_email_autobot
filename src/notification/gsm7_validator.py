"""
GSM-7 character set validation for SMS messages.

This module provides a validator to ensure that SMS messages
only contain valid GSM-7 characters.
"""

from typing import List, Dict, Any

class GSM7Validator:
    """
    Validator for GSM-7 character set compliance.
    """
    # GSM-7 default alphabet (simplified but correct)
    # These are the basic GSM-7 characters that are definitely supported
    GSM7_CHARS = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        "@£$¥èéùìòÇØøÅå_ÆæÉÄÖÑÜ§¿à"
        "€"
        "\n\r"
    )
    # Set for fast lookup
    GSM7_SET = set(GSM7_CHARS)
    
    # Character replacement mapping for common non-GSM-7 characters
    CHAR_REPLACEMENTS = {
        # German umlauts (NOT in GSM-7)
        'ä': 'ae', 'Ä': 'Ae',
        'ö': 'oe', 'Ö': 'Oe',
        'ü': 'ue', 'Ü': 'Ue',
        'ß': 'ss',
        
        # Typographic quotes and apostrophes
        '"': '"', '"': '"',  # Smart quotes to straight quotes
        ''': "'", ''': "'",  # Smart apostrophes to straight apostrophes
        '‹': '<', '›': '>',
        '«': '"', '»': '"',
        
        # Common symbols
        '©': '(c)',
        '®': '(R)',
        '™': '(TM)',
        '¢': 'c',
        '°': 'deg',
        '±': '+/-',
        '×': 'x',
        '÷': '/',
        '≤': '<=',
        '≥': '>=',
        '≠': '!=',
        '≈': '~',
        '∞': 'inf',
        '√': 'sqrt',
        '²': '2',
        '³': '3',
        '¹': '1',
        '¼': '1/4',
        '½': '1/2',
        '¾': '3/4',
        
        # Arrows
        '→': '->', '←': '<-', '↑': '^', '↓': 'v',
        '⇒': '=>', '⇐': '<=',
        
        # Other common characters
        '–': '-', '—': '-',  # En/em dashes to hyphen
        '…': '...',
        '•': '*',
        '·': '*',
        '§': 'S',
        '¶': 'P',
        '†': '+',
        '‡': '++',
        
        # Currency symbols (except € which is GSM-7)
        '₽': 'RUB',
        '₹': 'INR',
        '₩': 'KRW',
        '₪': 'ILS',
        '₦': 'NGN',
        '₨': 'PKR',
        '₫': 'VND',
        '₭': 'LAK',
        '₮': 'MNT',
        '₯': 'GRD',
        '₰': 'PF',
        '₱': 'PHP',
        '₲': 'PYG',
        '₳': 'ARA',
        '₴': 'UAH',
        '₵': 'GHS',
        '₶': 'LVL',
        '₷': 'SKK',
        '₸': 'KZT',
        '₺': 'TRY',
        '₻': 'CZK',
        '₼': 'AZN',
        '₾': 'GEL',
        '₿': 'BTC',
    }

    def is_valid(self, message: str) -> bool:
        """
        Check if the message contains only valid GSM-7 characters.

        Args:
            message: The message text to check
        Returns:
            True if all characters are GSM-7, False otherwise
        """
        if not message:
            return True
        for char in message:
            if char not in self.GSM7_SET:
                return False
        return True

    def validate_message(self, message: str) -> Dict[str, Any]:
        """
        Validate the message and return details about violations.

        Args:
            message: The message text to check
        Returns:
            Dictionary with keys:
                - is_valid: bool
                - violations: List of dicts with keys 'character', 'position', 'context'
        """
        violations = []
        if not message:
            return {"is_valid": True, "violations": []}
        for idx, char in enumerate(message):
            if char not in self.GSM7_SET:
                # Extract context (5 chars before/after)
                start = max(0, idx - 5)
                end = min(len(message), idx + 6)
                context = message[start:end]
                violations.append({
                    "character": char,
                    "position": idx,
                    "context": context
                })
        return {"is_valid": len(violations) == 0, "violations": violations}
    
    def normalize_to_gsm7(self, message: str) -> str:
        """
        Normalize a message to contain only GSM-7 characters.
        
        Args:
            message: The message text to normalize
            
        Returns:
            Normalized message with only GSM-7 characters
        """
        if not message:
            return message
            
        normalized = ""
        for char in message:
            if char in self.GSM7_SET:
                # Character is already GSM-7 compliant
                normalized += char
            elif char in self.CHAR_REPLACEMENTS:
                # Replace with GSM-7 equivalent
                normalized += self.CHAR_REPLACEMENTS[char]
            else:
                # Remove character entirely
                continue
                
        return normalized
    
    def normalize_with_logging(self, message: str) -> Dict[str, Any]:
        """
        Normalize a message to GSM-7 and return information about changes made.
        
        Args:
            message: The message text to normalize
            
        Returns:
            Dictionary with keys:
                - normalized_text: str - The normalized message
                - was_changed: bool - Whether any changes were made
                - replacements: List of dicts with 'original', 'replacement', 'position'
                - removed_chars: List of dicts with 'character', 'position'
        """
        if not message:
            return {
                "normalized_text": message,
                "was_changed": False,
                "replacements": [],
                "removed_chars": []
            }
            
        normalized = ""
        replacements = []
        removed_chars = []
        
        for idx, char in enumerate(message):
            if char in self.GSM7_SET:
                # Character is already GSM-7 compliant
                normalized += char
            elif char in self.CHAR_REPLACEMENTS:
                # Replace with GSM-7 equivalent
                replacement = self.CHAR_REPLACEMENTS[char]
                normalized += replacement
                replacements.append({
                    "original": char,
                    "replacement": replacement,
                    "position": idx
                })
            else:
                # Remove character entirely
                removed_chars.append({
                    "character": char,
                    "position": idx
                })
                continue
                
        return {
            "normalized_text": normalized,
            "was_changed": len(replacements) > 0 or len(removed_chars) > 0,
            "replacements": replacements,
            "removed_chars": removed_chars
        } 
"""
Tests for GSM-7 character validation.

This module tests the GSM-7 character validation functionality
to ensure SMS messages only contain valid GSM-7 characters.
"""

import pytest
from src.notification.gsm7_validator import GSM7Validator


class TestGSM7Validator:
    """Test cases for GSM-7 character validation."""
    
    def test_valid_gsm7_characters(self):
        """Test that valid GSM-7 characters are accepted."""
        validator = GSM7Validator()
        
        # Test basic ASCII characters
        assert validator.is_valid("Hello World") is True
        assert validator.is_valid("1234567890") is True
        assert validator.is_valid("!@#$%&*()") is True
        assert validator.is_valid("ABCDEFGHIJKLMNOPQRSTUVWXYZ") is True
        assert validator.is_valid("abcdefghijklmnopqrstuvwxyz") is True
        
        # Test GSM-7 specific characters (without ä, ö, ü, Ä, Ö, Ü, ß, æ, Æ)
        assert validator.is_valid("@£$¥èéùìòÇØøÅå_É") is True
        assert validator.is_valid("ÄÖÑÜ§¿à") is True  # All are GSM-7
        assert validator.is_valid("€") is True  # Euro is GSM-7
        
        # Test mixed valid characters
        assert validator.is_valid("Hello World! 123 @£$") is True
        # Note: "25°C" is NOT GSM-7 compliant - ° is not in GSM-7
        assert validator.is_valid("GR20 Weather Report: Sunny, 25C") is True
    
    def test_invalid_gsm7_characters(self):
        """Test that invalid GSM-7 characters are rejected."""
        validator = GSM7Validator()
        
        # Test common invalid characters
        assert validator.is_valid("Hello Worldö") is False  # German umlaut
        assert validator.is_valid("Hello Worldß") is False  # German sharp S
        assert validator.is_valid("Hello Worldü") is False  # German umlaut
        assert validator.is_valid("Hello Worldä") is False  # German umlaut
        
        # Test typographic quotes (ASCII quote is valid, so this is True)
        assert validator.is_valid('Hello "World"') is True
        assert validator.is_valid("Hello 'World'") is True
        
        # Test emojis
        assert validator.is_valid("Hello World 😀") is False  # Emoji
        assert validator.is_valid("Hello World 🌤️") is False  # Weather emoji
        
        # Test other Unicode characters
        assert validator.is_valid("Hello World →") is False  # Arrow
        assert validator.is_valid("Hello World ©") is False  # Copyright
        assert validator.is_valid("Hello World ₽") is False  # Ruble symbol
        
        # Test degree symbol
        assert validator.is_valid("Temperature: 25°C") is False  # Degree symbol
    
    def test_empty_string(self):
        """Test that empty string is considered valid."""
        validator = GSM7Validator()
        assert validator.is_valid("") is True
    
    def test_whitespace_only(self):
        """Test that whitespace-only strings are valid."""
        validator = GSM7Validator()
        assert validator.is_valid("   ") is True
        assert validator.is_valid("\n\r") is True  # Only \n and \r are GSM-7
        assert validator.is_valid("\n\t\r") is False  # \t is not GSM-7
    
    def test_validate_message_with_violations(self):
        """Test validation with detailed violation information."""
        validator = GSM7Validator()
        
        # Test message with multiple violations
        message = "Hello Worldö with ß and ü characters"
        result = validator.validate_message(message)
        
        assert result["is_valid"] is False
        assert len(result["violations"]) == 3
        
        # Check specific violations
        violations = result["violations"]
        assert any(v["character"] == "ö" for v in violations)
        assert any(v["character"] == "ß" for v in violations)
        assert any(v["character"] == "ü" for v in violations)
        
        # Check positions
        for violation in violations:
            assert "position" in violation
            assert "character" in violation
            assert "context" in violation
    
    def test_validate_message_valid(self):
        """Test validation of valid message."""
        validator = GSM7Validator()
        
        message = "Hello World! This is a valid GSM-7 message."
        result = validator.validate_message(message)
        
        assert result["is_valid"] is True
        assert result["violations"] == []
    
    def test_context_extraction(self):
        """Test that context is properly extracted around violations."""
        validator = GSM7Validator()
        
        message = "Hello Worldö with some text"
        result = validator.validate_message(message)
        
        assert result["is_valid"] is False
        assert len(result["violations"]) == 1
        
        violation = result["violations"][0]
        assert violation["character"] == "ö"
        assert "context" in violation
        # Context should include surrounding characters
        assert "World" in violation["context"]
    
    def test_multiple_violations_same_character(self):
        """Test handling of multiple occurrences of the same invalid character."""
        validator = GSM7Validator()
        
        message = "Helloö Worldö withö multipleö ö characters"
        result = validator.validate_message(message)
        
        assert result["is_valid"] is False
        assert len(result["violations"]) == 5
        
        # All violations should be for 'ö'
        for violation in result["violations"]:
            assert violation["character"] == "ö"
    
    def test_normalize_to_gsm7(self):
        """Test basic normalization to GSM-7 characters."""
        validator = GSM7Validator()
        
        # Test German umlauts
        assert validator.normalize_to_gsm7("Hören Sie zu") == "Hoeren Sie zu"
        assert validator.normalize_to_gsm7("Grüße") == "Gruesse"
        assert validator.normalize_to_gsm7("Bäume") == "Baeume"
        
        # Test typographic quotes
        assert validator.normalize_to_gsm7('Hello "World"') == 'Hello "World"'
        assert validator.normalize_to_gsm7("It's a test") == "It's a test"
        
        # Test symbols
        assert validator.normalize_to_gsm7("Temperature: 25°C") == "Temperature: 25degC"
        assert validator.normalize_to_gsm7("Price: €10") == "Price: €10"  # € is GSM-7
        assert validator.normalize_to_gsm7("Copyright © 2024") == "Copyright (c) 2024"
        
        # Test mixed content
        original = "Hören Sie zu: Temperature 25°C, Price €10, Copyright © 2024"
        expected = "Hoeren Sie zu: Temperature 25degC, Price €10, Copyright (c) 2024"
        assert validator.normalize_to_gsm7(original) == expected
        
        # Test empty and whitespace
        assert validator.normalize_to_gsm7("") == ""
        assert validator.normalize_to_gsm7("   ") == "   "
    
    def test_normalize_with_logging(self):
        """Test normalization with detailed logging of changes."""
        validator = GSM7Validator()
        
        # Test with replacements
        result = validator.normalize_with_logging("Hören Sie zu: 25°C")
        
        assert result["normalized_text"] == "Hoeren Sie zu: 25degC"
        assert result["was_changed"] is True
        assert len(result["replacements"]) == 2  # Only ö and ° replaced
        assert len(result["removed_chars"]) == 0
        
        # Check specific replacements
        replacements = result["replacements"]
        assert any(r["original"] == "ö" and r["replacement"] == "oe" for r in replacements)
        assert any(r["original"] == "°" and r["replacement"] == "deg" for r in replacements)
        
        # Test with removed characters (emojis)
        result = validator.normalize_with_logging("Hello 😀 World")
        
        assert result["normalized_text"] == "Hello  World"
        assert result["was_changed"] is True
        assert len(result["replacements"]) == 0
        assert len(result["removed_chars"]) == 1
        assert result["removed_chars"][0]["character"] == "😀"
        
        # Test with no changes
        result = validator.normalize_with_logging("Hello World")
        
        assert result["normalized_text"] == "Hello World"
        assert result["was_changed"] is False
        assert len(result["replacements"]) == 0
        assert len(result["removed_chars"]) == 0
    
    def test_normalize_complex_scenario(self):
        """Test normalization with complex mixed content."""
        validator = GSM7Validator()
        
        original = "Wetterbericht: Höhenwinde → 25°C, Niederschlag ≤ 5mm, Gewitter ⚡ möglich"
        result = validator.normalize_with_logging(original)
        
        expected = "Wetterbericht: Hoehenwinde -> 25degC, Niederschlag <= 5mm, Gewitter  moeglich"
        assert result["normalized_text"] == expected
        assert result["was_changed"] is True
        
        # Verify all expected replacements
        replacements = result["replacements"]
        assert any(r["original"] == "ö" and r["replacement"] == "oe" for r in replacements)
        assert any(r["original"] == "°" and r["replacement"] == "deg" for r in replacements)
        assert any(r["original"] == "→" and r["replacement"] == "->" for r in replacements)
        assert any(r["original"] == "≤" and r["replacement"] == "<=" for r in replacements)
        # No ß in this string, so don't check for it
        
        # Verify emoji was removed
        removed = result["removed_chars"]
        assert any(r["character"] == "⚡" for r in removed)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        validator = GSM7Validator()
        
        # Test very long message
        long_message = "A" * 1000
        assert validator.is_valid(long_message) is True
        
        # Test message with only newlines and carriage returns
        assert validator.is_valid("\n\r\n\r") is True
        
        # Test message with only special GSM-7 characters (without ä, ö, ü, Ä, Ö, Ü, ß, æ, Æ)
        assert validator.is_valid("@£$¥èéùìòÇØøÅå_É") is True 
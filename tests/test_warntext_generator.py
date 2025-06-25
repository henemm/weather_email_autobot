import pytest
import math
from src.wetter.warntext_generator import generate_warntext


class TestWarntextGenerator:
    """Test cases for the generate_warntext function."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.config = {
            "warn_thresholds": {
                "info": 0.3,
                "warning": 0.6,
                "critical": 0.9
            }
        }
    
    def test_risk_zero_returns_none(self):
        """Test that risk value of 0.0 returns None."""
        result = generate_warntext(0.0, self.config)
        assert result is None
    
    def test_risk_below_info_threshold_returns_none(self):
        """Test that risk value below info threshold returns None."""
        result = generate_warntext(0.2, self.config)
        assert result is None
    
    def test_risk_at_info_threshold_returns_info_text(self):
        """Test that risk value at info threshold returns info text."""
        result = generate_warntext(0.3, self.config)
        assert result is not None
        assert "⚠️" in result
        assert "Leicht erhöhte Wettergefahr" in result
    
    def test_risk_above_info_below_warning_returns_info_text(self):
        """Test that risk value between info and warning thresholds returns info text."""
        result = generate_warntext(0.4, self.config)
        assert result is not None
        assert "⚠️" in result
        assert "Leicht erhöhte Wettergefahr" in result
    
    def test_risk_at_warning_threshold_returns_warning_text(self):
        """Test that risk value at warning threshold returns warning text."""
        result = generate_warntext(0.6, self.config)
        assert result is not None
        assert "⚠️" in result
        assert "Warnung:" in result
        assert "Das Wetter-Risiko liegt bei" in result
    
    def test_risk_above_warning_below_critical_returns_warning_text(self):
        """Test that risk value between warning and critical thresholds returns warning text."""
        result = generate_warntext(0.7, self.config)
        assert result is not None
        assert "⚠️" in result
        assert "Warnung:" in result
        assert "Das Wetter-Risiko liegt bei" in result
    
    def test_risk_at_critical_threshold_returns_alarm_text(self):
        """Test that risk value at critical threshold returns alarm text."""
        result = generate_warntext(0.9, self.config)
        assert result is not None
        assert "🚨" in result
        assert "Alarm!" in result
        assert "Sehr hohes Wetterrisiko" in result
    
    def test_risk_above_critical_returns_alarm_text(self):
        """Test that risk value above critical threshold returns alarm text."""
        result = generate_warntext(0.95, self.config)
        assert result is not None
        assert "🚨" in result
        assert "Alarm!" in result
        assert "Sehr hohes Wetterrisiko" in result
    
    def test_risk_maximum_returns_alarm_text(self):
        """Test that risk value of 1.0 returns alarm text."""
        result = generate_warntext(1.0, self.config)
        assert result is not None
        assert "🚨" in result
        assert "Alarm!" in result
        assert "Sehr hohes Wetterrisiko" in result
    
    def test_empty_config_raises_exception(self):
        """Test that empty configuration raises an exception."""
        with pytest.raises(ValueError):
            generate_warntext(0.5, {})
    
    def test_missing_warn_thresholds_raises_exception(self):
        """Test that missing warn_thresholds in config raises an exception."""
        config = {"other_key": "value"}
        with pytest.raises(ValueError):
            generate_warntext(0.5, config)
    
    def test_incomplete_thresholds_raises_exception(self):
        """Test that incomplete thresholds raise an exception."""
        config = {"warn_thresholds": {"info": 0.3}}
        with pytest.raises(ValueError):
            generate_warntext(0.5, config)
    
    def test_negative_risk_raises_exception(self):
        """Test that negative risk value raises an exception."""
        with pytest.raises(ValueError):
            generate_warntext(-0.1, self.config)
    
    def test_risk_above_one_raises_exception(self):
        """Test that risk value above 1.0 raises an exception."""
        with pytest.raises(ValueError):
            generate_warntext(1.1, self.config)
    
    def test_nan_risk_raises_exception(self):
        """Test that NaN risk value raises an exception."""
        with pytest.raises(ValueError):
            generate_warntext(float('nan'), self.config)
    
    def test_infinity_risk_raises_exception(self):
        """Test that infinity risk value raises an exception."""
        with pytest.raises(ValueError):
            generate_warntext(float('inf'), self.config)
    
    def test_generated_warning_text_is_emoji_free(self):
        """Test that generated warning text is emoji-free."""
        # Test with different risk levels
        test_cases = [
            (0.4, "info"),
            (0.7, "warning"), 
            (0.95, "critical")
        ]
        
        emoji_chars = ["⚠️", "⚡", "🌤️", "🚨", "🌧️", "🌩️", "🌪️", "🌊", "❄️", "☀️", "⛈️", "🌨️", "💨", "🌫️", "🌡️", "💧", "🏔️", "🌋"]
        
        for risk_value, expected_level in test_cases:
            result = generate_warntext(risk_value, self.config)
            
            assert result is not None
            
            # Check that no emojis are present
            for emoji in emoji_chars:
                assert emoji not in result, f"Emoji '{emoji}' found in {expected_level} level warning"
            
            # Verify the text still contains the essential information
            assert "Wettergefahr" in result or "WARNUNG" in result or "ALARM" in result
            assert f"{int(risk_value * 100)}%" in result
            
            # Check for text-based indicators instead of emojis
            if expected_level == "info":
                assert "WARNUNG" in result and "Leicht erhöhte Wettergefahr" in result
            elif expected_level == "warning":
                assert "WARNUNG" in result and "Das Wetter-Risiko liegt bei" in result
            elif expected_level == "critical":
                assert "ALARM" in result and "Sehr hohes Wetterrisiko" in result 
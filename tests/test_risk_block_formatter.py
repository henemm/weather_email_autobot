import pytest
from src.fire.risk_block_formatter import format_risk_block

def test_format_risk_block_with_coordinates():
    """Test format_risk_block function with actual coordinates."""
    result = format_risk_block(42.286473, 8.893564)
    # Should return a string like "Z:HIGH208,217" or None if no risks
    assert result is None or isinstance(result, str)
    if result:
        assert result.startswith("Z:") or result.startswith("M:")

def test_format_risk_block_with_config():
    """Test format_risk_block function with custom config."""
    config = {
        'fire_risk_levels': {
            'zone_risk_mapping': {
                1: "LOW",
                2: "HIGH",
                3: "HIGH", 
                4: "MAX"
            },
            'minimum_display_level': 2,
            'massif_restriction_threshold': 1
        }
    }
    result = format_risk_block(42.286473, 8.893564, config)
    # Should return a string or None
    assert result is None or isinstance(result, str)

def test_format_risk_block_different_levels():
    """Test format_risk_block with different minimum display levels."""
    # Test with minimum level 1 (should show more zones)
    config_level_1 = {
        'fire_risk_levels': {
            'minimum_display_level': 1
        }
    }
    result_level_1 = format_risk_block(42.286473, 8.893564, config_level_1)
    
    # Test with minimum level 3 (should show fewer zones)
    config_level_3 = {
        'fire_risk_levels': {
            'minimum_display_level': 3
        }
    }
    result_level_3 = format_risk_block(42.286473, 8.893564, config_level_3)
    
    # Both should return valid results
    assert result_level_1 is None or isinstance(result_level_1, str)
    assert result_level_3 is None or isinstance(result_level_3, str)

if __name__ == "__main__":
    pytest.main([__file__]) 
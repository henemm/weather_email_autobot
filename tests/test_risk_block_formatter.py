import pytest
from src.utils.risk_block_formatter import format_risk_block

def test_only_high_zones():
    assert format_risk_block([204, 208], [], []) == "Z:HIGH204,208"

def test_only_max_zones():
    assert format_risk_block([], [209], []) == "MAX209"

def test_only_massifs():
    assert format_risk_block([], [], [3, 5, 9]) == "M:3,5,9"

def test_high_and_max_zones():
    assert format_risk_block([204, 208], [209], []) == "Z:HIGH204,208 MAX209"

def test_all():
    assert format_risk_block([204, 208], [209], [3, 5, 9]) == "Z:HIGH204,208 MAX209 M:3,5,9"

def test_empty():
    assert format_risk_block([], [], []) == ""

def test_ordering():
    # Should always be sorted
    assert format_risk_block([208, 204], [209], [9, 3, 5]) == "Z:HIGH204,208 MAX209 M:3,5,9" 
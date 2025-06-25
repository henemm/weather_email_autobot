import pytest
from datetime import datetime, timedelta
from typing import Dict, List

# Import the functions to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.analyse import (
    RegenRisiko, 
    WetterDaten, 
    RegenAnalyse,
    analysiere_regen_risiko,
    analysiere_regen_trend,
    generiere_regen_warnung
)


class TestRegenRisiko:
    """Test cases for rain risk analysis functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.base_config = {
            "schwellen": {
                "regen": 25,
                "regenmenge": 2
            }
        }
        
        self.base_time = datetime(2025, 6, 15, 12, 0)
        
    def test_regen_risiko_enum_values(self):
        """Test that RegenRisiko enum has correct values"""
        assert RegenRisiko.NIEDRIG.value == "niedrig"
        assert RegenRisiko.MITTEL.value == "mittel"
        assert RegenRisiko.HOCH.value == "hoch"
        assert RegenRisiko.SEHR_HOCH.value == "sehr_hoch"
    
    def test_wetter_daten_creation(self):
        """Test WetterDaten dataclass creation"""
        wetter = WetterDaten(
            datum=self.base_time,
            temperatur=20.0,
            niederschlag_prozent=30.0,
            niederschlag_mm=5.0,
            wind_geschwindigkeit=15.0,
            luftfeuchtigkeit=75.0
        )
        
        assert wetter.datum == self.base_time
        assert wetter.temperatur == 20.0
        assert wetter.niederschlag_prozent == 30.0
        assert wetter.niederschlag_mm == 5.0
        assert wetter.wind_geschwindigkeit == 15.0
        assert wetter.luftfeuchtigkeit == 75.0
    
    def test_analysiere_regen_risiko_empty_data(self):
        """Test rain risk analysis with empty weather data"""
        result = analysiere_regen_risiko([], self.base_config)
        
        assert result.risiko_stufe == RegenRisiko.NIEDRIG
        assert result.bewertung == "Keine Wetterdaten verfügbar"
        assert result.empfehlung == "Wetterdaten überprüfen"
        assert result.kritische_werte == []
        assert result.gesamt_risiko_score == 0.0
    
    def test_analysiere_regen_risiko_niedrig(self):
        """Test low rain risk scenario"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=25.0,
                niederschlag_prozent=10.0,  # Below threshold
                niederschlag_mm=0.5,        # Below threshold
                wind_geschwindigkeit=10.0,
                luftfeuchtigkeit=60.0
            )
        ]
        
        result = analysiere_regen_risiko(wetter_daten, self.base_config)
        
        assert result.risiko_stufe == RegenRisiko.NIEDRIG
        assert "Niedriges Regenrisiko" in result.bewertung
        assert "Normale Aktivitäten möglich" in result.empfehlung
        assert result.gesamt_risiko_score < 0.3
        assert len(result.kritische_werte) == 0
    
    def test_analysiere_regen_risiko_mittel(self):
        """Test medium rain risk scenario"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=18.0,
                niederschlag_prozent=30.0,  # Above threshold
                niederschlag_mm=1.0,        # Below threshold
                wind_geschwindigkeit=20.0,
                luftfeuchtigkeit=70.0
            )
        ]
        
        result = analysiere_regen_risiko(wetter_daten, self.base_config)
        
        assert result.risiko_stufe == RegenRisiko.MITTEL
        assert "Mittleres Regenrisiko" in result.bewertung
        assert "Leichten Regenschutz bereithalten" in result.empfehlung
        assert 0.3 <= result.gesamt_risiko_score < 0.6
        assert len(result.kritische_werte) == 1
    
    def test_analysiere_regen_risiko_hoch(self):
        """Test high rain risk scenario"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=15.0,
                niederschlag_prozent=40.0,  # Above threshold
                niederschlag_mm=3.0,        # Above threshold
                wind_geschwindigkeit=25.0,
                luftfeuchtigkeit=85.0
            )
        ]
        
        result = analysiere_regen_risiko(wetter_daten, self.base_config)
        
        assert result.risiko_stufe == RegenRisiko.HOCH
        assert "Hohes Regenrisiko" in result.bewertung
        assert "Regenschutz mitnehmen" in result.empfehlung
        assert 0.6 <= result.gesamt_risiko_score < 0.8
        assert len(result.kritische_werte) == 2
    
    def test_analysiere_regen_risiko_sehr_hoch(self):
        """Test very high rain risk scenario"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=12.0,
                niederschlag_prozent=80.0,  # Well above threshold
                niederschlag_mm=8.0,        # Well above threshold
                wind_geschwindigkeit=35.0,  # Above wind threshold
                luftfeuchtigkeit=90.0       # Above humidity threshold
            )
        ]
        
        result = analysiere_regen_risiko(wetter_daten, self.base_config)
        
        assert result.risiko_stufe == RegenRisiko.SEHR_HOCH
        assert "Sehr hohes Regenrisiko" in result.bewertung
        assert "Aktivitäten im Freien vermeiden" in result.empfehlung
        assert result.gesamt_risiko_score >= 0.8
        assert len(result.kritische_werte) == 2
    
    def test_analysiere_regen_risiko_multiple_data_points(self):
        """Test rain risk analysis with multiple weather data points"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=20.0,
                niederschlag_prozent=20.0,
                niederschlag_mm=1.0,
                wind_geschwindigkeit=15.0,
                luftfeuchtigkeit=70.0
            ),
            WetterDaten(
                datum=self.base_time + timedelta(hours=3),
                temperatur=18.0,
                niederschlag_prozent=35.0,  # Above threshold
                niederschlag_mm=2.5,        # Above threshold
                wind_geschwindigkeit=20.0,
                luftfeuchtigkeit=80.0
            ),
            WetterDaten(
                datum=self.base_time + timedelta(hours=6),
                temperatur=16.0,
                niederschlag_prozent=25.0,
                niederschlag_mm=1.5,
                wind_geschwindigkeit=25.0,
                luftfeuchtigkeit=75.0
            )
        ]
        
        result = analysiere_regen_risiko(wetter_daten, self.base_config)
        
        assert result.risiko_stufe in [RegenRisiko.MITTEL, RegenRisiko.HOCH]
        assert "35.0%" in result.bewertung  # Max precipitation probability (with decimal)
        assert "2.5mm" in result.bewertung  # Max precipitation amount
        assert len(result.kritische_werte) >= 1
    
    def test_analysiere_regen_risiko_custom_thresholds(self):
        """Test rain risk analysis with custom thresholds"""
        custom_config = {
            "schwellen": {
                "regen": 15,      # Lower threshold
                "regenmenge": 1   # Lower threshold
            }
        }
        
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=20.0,
                niederschlag_prozent=20.0,  # Above custom threshold
                niederschlag_mm=1.5,        # Above custom threshold
                wind_geschwindigkeit=15.0,
                luftfeuchtigkeit=70.0
            )
        ]
        
        result = analysiere_regen_risiko(wetter_daten, custom_config)
        
        assert result.risiko_stufe in [RegenRisiko.MITTEL, RegenRisiko.HOCH]
        assert len(result.kritische_werte) == 2
    
    def test_analysiere_regen_trend_increasing(self):
        """Test trend analysis with increasing rain probability"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=20.0,
                niederschlag_prozent=10.0,
                niederschlag_mm=1.0,
                wind_geschwindigkeit=15.0,
                luftfeuchtigkeit=70.0
            ),
            WetterDaten(
                datum=self.base_time + timedelta(hours=3),
                temperatur=18.0,
                niederschlag_prozent=30.0,
                niederschlag_mm=2.0,
                wind_geschwindigkeit=20.0,
                luftfeuchtigkeit=75.0
            )
        ]
        
        result = analysiere_regen_trend(wetter_daten)
        
        assert result["trend"] == "zunehmend"
        assert result["aenderung"] > 10
        assert result["durchschnitt_anfang"] == 10.0
        assert result["durchschnitt_ende"] == 30.0
    
    def test_analysiere_regen_trend_decreasing(self):
        """Test trend analysis with decreasing rain probability"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=18.0,
                niederschlag_prozent=40.0,
                niederschlag_mm=3.0,
                wind_geschwindigkeit=20.0,
                luftfeuchtigkeit=80.0
            ),
            WetterDaten(
                datum=self.base_time + timedelta(hours=3),
                temperatur=20.0,
                niederschlag_prozent=15.0,
                niederschlag_mm=1.0,
                wind_geschwindigkeit=15.0,
                luftfeuchtigkeit=70.0
            )
        ]
        
        result = analysiere_regen_trend(wetter_daten)
        
        assert result["trend"] == "abnehmend"
        assert result["aenderung"] < -10
        assert result["durchschnitt_anfang"] == 40.0
        assert result["durchschnitt_ende"] == 15.0
    
    def test_analysiere_regen_trend_stable(self):
        """Test trend analysis with stable rain probability"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=20.0,
                niederschlag_prozent=25.0,
                niederschlag_mm=2.0,
                wind_geschwindigkeit=15.0,
                luftfeuchtigkeit=70.0
            ),
            WetterDaten(
                datum=self.base_time + timedelta(hours=3),
                temperatur=19.0,
                niederschlag_prozent=30.0,
                niederschlag_mm=2.5,
                wind_geschwindigkeit=18.0,
                luftfeuchtigkeit=72.0
            )
        ]
        
        result = analysiere_regen_trend(wetter_daten)
        
        assert result["trend"] == "stabil"
        assert abs(result["aenderung"]) <= 10
    
    def test_analysiere_regen_trend_single_data_point(self):
        """Test trend analysis with insufficient data"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=20.0,
                niederschlag_prozent=25.0,
                niederschlag_mm=2.0,
                wind_geschwindigkeit=15.0,
                luftfeuchtigkeit=70.0
            )
        ]
        
        result = analysiere_regen_trend(wetter_daten)
        
        assert result["trend"] == "unbekannt"
        assert result["aenderung"] == 0.0
    
    def test_generiere_regen_warnung_complete(self):
        """Test warning generation with complete analysis data"""
        analyse = RegenAnalyse(
            risiko_stufe=RegenRisiko.HOCH,
            bewertung="Hohes Regenrisiko. Max. Regenwahrscheinlichkeit: 40%, Max. Niederschlag: 3mm",
            empfehlung="Regenschutz mitnehmen. Alternative Indoor-Aktivitäten planen.",
            kritische_werte=[
                "Regenwahrscheinlichkeit 40% am 15.06.2025 12:00",
                "Niederschlagsmenge 3mm am 15.06.2025 12:00"
            ],
            gesamt_risiko_score=0.7
        )
        
        trend = {
            "trend": "zunehmend",
            "aenderung": 15.5,
            "durchschnitt_anfang": 20.0,
            "durchschnitt_ende": 35.5
        }
        
        warnung = generiere_regen_warnung(analyse, trend)
        
        # Verify the warning contains expected content
        assert "REGENRISIKO-ANALYSE" in warnung
        assert "Risikostufe: HOCH" in warnung
        assert "Score: 0.7/1.0" in warnung
        assert "Hohes Regenrisiko" in warnung
        assert "Regenschutz mitnehmen" in warnung
        assert "zunehmend (+15.5%)" in warnung
        assert "Regenwahrscheinlichkeit 40%" in warnung
        assert "Niederschlagsmenge 3mm" in warnung
        
        # Check that warning is emoji-free
        emoji_chars = ["⚠️", "⚡", "🌤️", "🚨", "🌧️", "🌩️", "🌪️", "🌊", "❄️", "☀️", "⛈️", "🌨️", "💨", "🌫️", "🌡️", "💧", "🏔️", "🌋"]
        for emoji in emoji_chars:
            assert emoji not in warnung, f"Emoji '{emoji}' found in analysis warning"
    
    def test_generiere_regen_warnung_stable_trend(self):
        """Test warning generation with stable trend"""
        analyse = RegenAnalyse(
            risiko_stufe=RegenRisiko.NIEDRIG,
            bewertung="Niedriges Regenrisiko. Gute Bedingungen für Outdoor-Aktivitäten.",
            empfehlung="Normale Aktivitäten möglich. Wetterlage bleibt stabil.",
            kritische_werte=[],
            gesamt_risiko_score=0.1
        )
        
        trend = {
            "trend": "stabil",
            "aenderung": 2.0,
            "durchschnitt_anfang": 20.0,
            "durchschnitt_ende": 22.0
        }
        
        warnung = generiere_regen_warnung(analyse, trend)
        
        assert "REGENRISIKO-ANALYSE" in warnung
        assert "Risikostufe: NIEDRIG" in warnung
        assert "Score: 0.1/1.0" in warnung
        assert "Niedriges Regenrisiko" in warnung
        assert "Normale Aktivitäten möglich" in warnung
        # Should not contain trend information for stable trend
        assert "Trend:" not in warnung
        assert "Kritische Werte:" not in warnung
        
        # Check that warning is emoji-free
        emoji_chars = ["⚠️", "⚡", "🌤️", "🚨", "🌧️", "🌩️", "🌪️", "🌊", "❄️", "☀️", "⛈️", "🌨️", "💨", "🌫️", "🌡️", "💧", "🏔️", "🌋"]
        for emoji in emoji_chars:
            assert emoji not in warnung, f"Emoji '{emoji}' found in analysis warning"
    
    def test_integration_full_workflow(self):
        """Test complete integration workflow"""
        wetter_daten = [
            WetterDaten(
                datum=self.base_time,
                temperatur=18.0,
                niederschlag_prozent=35.0,
                niederschlag_mm=4.0,
                wind_geschwindigkeit=25.0,
                luftfeuchtigkeit=85.0
            ),
            WetterDaten(
                datum=self.base_time + timedelta(hours=3),
                temperatur=16.0,
                niederschlag_prozent=45.0,
                niederschlag_mm=6.0,
                wind_geschwindigkeit=30.0,
                luftfeuchtigkeit=90.0
            )
        ]
        
        # Step 1: Analyze rain risk
        analyse = analysiere_regen_risiko(wetter_daten, self.base_config)
        
        # Step 2: Analyze trend
        trend = analysiere_regen_trend(wetter_daten)
        
        # Step 3: Generate warning
        warnung = generiere_regen_warnung(analyse, trend)
        
        # Verify results
        assert analyse.risiko_stufe in [RegenRisiko.HOCH, RegenRisiko.SEHR_HOCH]
        # The trend should be stable since 45% - 35% = 10% (exactly at threshold)
        assert trend["trend"] == "stabil"
        assert "REGENRISIKO-ANALYSE" in warnung
        assert len(analyse.kritische_werte) >= 2
        
        # Check that warning is emoji-free
        emoji_chars = ["⚠️", "⚡", "🌤️", "🚨", "🌧️", "🌩️", "🌪️", "🌊", "❄️", "☀️", "⛈️", "🌨️", "💨", "🌫️", "🌡️", "💧", "🏔️", "🌋"]
        for emoji in emoji_chars:
            assert emoji not in warnung, f"Emoji '{emoji}' found in analysis warning"

# TODO: Add rain risk analysis

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from utils.logging_setup import get_logger
except ImportError:
    try:
        from src.utils.logging_setup import get_logger
    except ImportError:
        from ..utils.logging_setup import get_logger

logger = get_logger(__name__)


class RegenRisiko(Enum):
    """Enum für verschiedene Regenrisiko-Stufen"""
    NIEDRIG = "niedrig"
    MITTEL = "mittel"
    HOCH = "hoch"
    SEHR_HOCH = "sehr_hoch"


@dataclass
class WetterDaten:
    """Dataclass für Wetterdaten"""
    datum: datetime
    temperatur: float
    niederschlag_prozent: float  # Regenwahrscheinlichkeit in %
    niederschlag_mm: float  # Niederschlagsmenge in mm
    wind_geschwindigkeit: float  # Windgeschwindigkeit in km/h
    luftfeuchtigkeit: float  # Luftfeuchtigkeit in %


@dataclass
class RegenAnalyse:
    """Dataclass für Regenanalyse-Ergebnisse"""
    risiko_stufe: RegenRisiko
    bewertung: str
    empfehlung: str
    kritische_werte: List[str]
    gesamt_risiko_score: float  # 0.0 bis 1.0


def analysiere_regen_risiko(
    wetter_daten: List[WetterDaten], 
    config: Dict
) -> RegenAnalyse:
    """
    Analysiert das Regenrisiko basierend auf Wetterdaten und Konfiguration.
    
    Args:
        wetter_daten: Liste von Wetterdaten für verschiedene Zeitpunkte
        config: Konfigurationsdictionary mit Schwellenwerten
        
    Returns:
        RegenAnalyse: Analyseergebnis mit Risikobewertung
    """
    logger.info(f"Starting rain risk analysis with {len(wetter_daten)} weather data points")
    
    if not wetter_daten:
        logger.warning("No weather data provided for rain risk analysis")
        return RegenAnalyse(
            risiko_stufe=RegenRisiko.NIEDRIG,
            bewertung="Keine Wetterdaten verfügbar",
            empfehlung="Wetterdaten überprüfen",
            kritische_werte=[],
            gesamt_risiko_score=0.0
        )
    
    # Schwellenwerte aus Konfiguration extrahieren
    thresholds = config.get("thresholds", {})
    regen_schwelle = thresholds.get("rain_probability", 25)
    regenmenge_schwelle = thresholds.get("rain_amount", 2)
    
    logger.info(f"Using thresholds: rain probability {regen_schwelle}%, rain amount {regenmenge_schwelle}mm")
    
    kritische_werte = []
    risiko_score = 0.0
    max_niederschlag_prozent = 0.0
    max_niederschlag_mm = 0.0
    regen_stunden = 0
    
    # Analyse der Wetterdaten
    for wetter in wetter_daten:
        # Regenwahrscheinlichkeit prüfen
        if wetter.niederschlag_prozent > regen_schwelle:
            kritische_werte.append(
                f"Regenwahrscheinlichkeit {wetter.niederschlag_prozent}% "
                f"am {wetter.datum.strftime('%d.%m.%Y %H:%M')}"
            )
            risiko_score += 0.3
            max_niederschlag_prozent = max(max_niederschlag_prozent, wetter.niederschlag_prozent)
            logger.debug(f"High rain probability detected: {wetter.niederschlag_prozent}% at {wetter.datum}")
        
        # Niederschlagsmenge prüfen
        if wetter.niederschlag_mm > regenmenge_schwelle:
            kritische_werte.append(
                f"Niederschlagsmenge {wetter.niederschlag_mm}mm "
                f"am {wetter.datum.strftime('%d.%m.%Y %H:%M')}"
            )
            risiko_score += 0.4
            max_niederschlag_mm = max(max_niederschlag_mm, wetter.niederschlag_mm)
            regen_stunden += 1
            logger.debug(f"High rain amount detected: {wetter.niederschlag_mm}mm at {wetter.datum}")
        
        # Zusätzliche Risikofaktoren
        if wetter.luftfeuchtigkeit > 80:
            risiko_score += 0.1
            logger.debug(f"High humidity detected: {wetter.luftfeuchtigkeit}% at {wetter.datum}")
        if wetter.wind_geschwindigkeit > 30:
            risiko_score += 0.2
            logger.debug(f"High wind speed detected: {wetter.wind_geschwindigkeit} km/h at {wetter.datum}")
    
    # Risikostufe bestimmen
    if risiko_score >= 0.8:
        risiko_stufe = RegenRisiko.SEHR_HOCH
        bewertung = f"Sehr hohes Regenrisiko! Max. Regenwahrscheinlichkeit: {max_niederschlag_prozent}%, Max. Niederschlag: {max_niederschlag_mm}mm"
        empfehlung = "Aktivitäten im Freien vermeiden. Schutzkleidung und Regenschutz mitnehmen."
        logger.warning(f"Very high rain risk detected: score {risiko_score:.2f}")
    elif risiko_score >= 0.6:
        risiko_stufe = RegenRisiko.HOCH
        bewertung = f"Hohes Regenrisiko. Max. Regenwahrscheinlichkeit: {max_niederschlag_prozent}%, Max. Niederschlag: {max_niederschlag_mm}mm"
        empfehlung = "Regenschutz mitnehmen. Alternative Indoor-Aktivitäten planen."
        logger.warning(f"High rain risk detected: score {risiko_score:.2f}")
    elif risiko_score >= 0.3:
        risiko_stufe = RegenRisiko.MITTEL
        bewertung = f"Mittleres Regenrisiko. Max. Regenwahrscheinlichkeit: {max_niederschlag_prozent}%, Max. Niederschlag: {max_niederschlag_mm}mm"
        empfehlung = "Leichten Regenschutz bereithalten. Wetterlage beobachten."
        logger.info(f"Medium rain risk detected: score {risiko_score:.2f}")
    else:
        risiko_stufe = RegenRisiko.NIEDRIG
        bewertung = "Niedriges Regenrisiko. Gute Bedingungen für Outdoor-Aktivitäten."
        empfehlung = "Normale Aktivitäten möglich. Wetterlage bleibt stabil."
        logger.info(f"Low rain risk detected: score {risiko_score:.2f}")
    
    logger.info(f"Rain risk analysis completed: {risiko_stufe.value} risk level, {len(kritische_werte)} critical values")
    
    return RegenAnalyse(
        risiko_stufe=risiko_stufe,
        bewertung=bewertung,
        empfehlung=empfehlung,
        kritische_werte=kritische_werte,
        gesamt_risiko_score=min(risiko_score, 1.0)
    )


def analysiere_regen_trend(
    wetter_daten: List[WetterDaten]
) -> Dict[str, any]:
    """
    Analysiert den Regen-Trend über Zeit.
    
    Args:
        wetter_daten: Liste von Wetterdaten
        
    Returns:
        Dictionary mit Trend-Informationen
    """
    logger.info(f"Starting rain trend analysis with {len(wetter_daten)} weather data points")
    
    if len(wetter_daten) < 2:
        logger.warning("Insufficient data points for trend analysis")
        return {"trend": "unbekannt", "aenderung": 0.0}
    
    # Sortiere nach Datum
    sortierte_daten = sorted(wetter_daten, key=lambda x: x.datum)
    
    # Berechne durchschnittliche Regenwahrscheinlichkeit für erste und zweite Hälfte
    mitte = len(sortierte_daten) // 2
    erste_haelfte = sortierte_daten[:mitte]
    zweite_haelfte = sortierte_daten[mitte:]
    
    avg_erste = sum(w.niederschlag_prozent for w in erste_haelfte) / len(erste_haelfte)
    avg_zweite = sum(w.niederschlag_prozent for w in zweite_haelfte) / len(zweite_haelfte)
    
    aenderung = avg_zweite - avg_erste
    
    if aenderung > 10:
        trend = "zunehmend"
        logger.info(f"Rain trend: increasing ({aenderung:+.1f}%)")
    elif aenderung < -10:
        trend = "abnehmend"
        logger.info(f"Rain trend: decreasing ({aenderung:+.1f}%)")
    else:
        trend = "stabil"
        logger.info(f"Rain trend: stable ({aenderung:+.1f}%)")
    
    return {
        "trend": trend,
        "aenderung": aenderung,
        "durchschnitt_anfang": avg_erste,
        "durchschnitt_ende": avg_zweite
    }


def generiere_regen_warnung(
    analyse: RegenAnalyse,
    trend: Dict[str, any]
) -> str:
    """
    Generiert eine benutzerfreundliche Regenwarnung.
    
    Args:
        analyse: RegenAnalyse-Objekt
        trend: Trend-Dictionary
        
    Returns:
        Formatierte Warnung als String
    """
    logger.info(f"Generating rain warning for {analyse.risiko_stufe.value} risk level")
    
    warnung = f"REGENRISIKO-ANALYSE\n\n"
    warnung += f"Risikostufe: {analyse.risiko_stufe.value.upper()}\n"
    warnung += f"Score: {analyse.gesamt_risiko_score:.1f}/1.0\n\n"
    warnung += f"Bewertung: {analyse.bewertung}\n\n"
    warnung += f"Empfehlung: {analyse.empfehlung}\n\n"
    
    if trend["trend"] != "stabil":
        warnung += f"Trend: {trend['trend']} ({trend['aenderung']:+.1f}%)\n\n"
    
    if analyse.kritische_werte:
        warnung += "Kritische Werte:\n"
        for wert in analyse.kritische_werte:
            warnung += f"• {wert}\n"
    
    logger.debug(f"Generated rain warning with {len(analyse.kritische_werte)} critical values")
    return warnung
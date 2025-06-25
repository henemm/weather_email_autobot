import os
import requests
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List

try:
    from src.auth.meteo_token_provider import MeteoTokenProvider
except ImportError:
    from auth.meteo_token_provider import MeteoTokenProvider


@dataclass
class WeatherAlert:
    type: str            # z. B. "Orages", "Vent"
    level: int           # 1=grün, 2=gelb, 3=orange, 4=rot
    start: datetime
    end: datetime


def fetch_warnings(lat: float, lon: float) -> List[WeatherAlert]:
    """
    Fetch weather warnings from Météo-France Vigilance API using OAuth2.
    
    Args:
        lat: Latitude in decimal degrees (-90 to 90)
        lon: Longitude in decimal degrees (-180 to 180)
        
    Returns:
        List[WeatherAlert]: List of active weather alerts for the location
        
    Raises:
        RuntimeError: If OAuth token is missing or API request fails
        Exception: If HTTP request fails or other errors occur
    """
    # Get OAuth token using the centralized token provider
    token_provider = MeteoTokenProvider()
    token = token_provider.get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    url = f"https://portail-api.meteofrance.fr/vigilance/public/bulletin?lat={lat}&lon={lon}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    results = []
    for entry in data.get("timelaps", []):
        for item in entry.get("max_colors", []):
            level = int(item.get("phenomenon_max_color_id", 0))
            if level < 2:
                continue

            alert = WeatherAlert(
                type=item.get("phenomenon_max_name", "unbekannt"),
                level=level,
                start=datetime.fromisoformat(entry["validity_start_date"]),
                end=datetime.fromisoformat(entry["validity_end_date"])
            )
            results.append(alert)

    return results


def fetch_vigilance_text_warnings() -> dict:
    """
    Fetch vigilance text warnings from Météo-France using the new endpoint.
    Returns:
        dict: Structured result with status, data, and error if any.
    """
    try:
        token_provider = MeteoTokenProvider()
        token = token_provider.get_token()
        url = "https://public-api.meteofrance.fr/public/DPVigilance/v1/textesvigilance/encours"
        headers = {
            "Authorization": f"Bearer {token}",
            "accept": "*/*"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def parse_vigilance_warnings(vigilance_data: dict) -> dict:
    """
    Parse vigilance warnings and extract structured information.
    
    Args:
        vigilance_data: Raw vigilance API response
        
    Returns:
        Structured warning information
    """
    if not vigilance_data or vigilance_data.get('status') != 'success':
        return {
            'status': 'error',
            'warnings': [],
            'summary': 'No vigilance data available'
        }
    
    data = vigilance_data.get('data', {})
    product = data.get('product', {})
    text_bloc_items = product.get('text_bloc_items', [])
    
    warnings = []
    corsica_warnings = []
    
    for item in text_bloc_items:
        domain_id = item.get('domain_id')
        domain_name = item.get('domain_name')
        bloc_items = item.get('bloc_items', [])
        
        domain_warnings = []
        
        for bloc_item in bloc_items:
            text_items = bloc_item.get('text_items', [])
            
            for text_item in text_items:
                term_items = text_item.get('term_items', [])
                
                for term in term_items:
                    risk_code = term.get('risk_code', '0')
                    risk_name = term.get('risk_name', 'Unknown')
                    hazard_name = term.get('hazard_name', 'Unknown')
                    start_time = term.get('start_time')
                    end_time = term.get('end_time')
                    
                    # Extract detailed warning text
                    warning_details = _extract_warning_details(term)
                    
                    # Only include actual warnings (level 2-4)
                    if risk_code in ['2', '3', '4']:
                        warning = {
                            'domain_id': domain_id,
                            'domain_name': domain_name,
                            'risk_level': int(risk_code),
                            'risk_name': risk_name,
                            'hazard': hazard_name,
                            'start_time': start_time,
                            'end_time': end_time,
                            'is_active': _is_warning_active(start_time, end_time),
                            'details': warning_details,
                            'german_summary': _translate_warning_to_german(warning_details, risk_name)
                        }
                        domain_warnings.append(warning)
        
        if domain_warnings:
            warnings.extend(domain_warnings)
            
            # Check if this is Corsica
            if domain_id in ['2A', '2B', 'CORSE']:
                corsica_warnings.extend(domain_warnings)
    
    return {
        'status': 'success',
        'total_warnings': len(warnings),
        'corsica_warnings': len(corsica_warnings),
        'active_warnings': len([w for w in warnings if w['is_active']]),
        'warnings': warnings,
        'corsica_details': corsica_warnings,
        'summary': _generate_warning_summary(warnings)
    }

def _extract_warning_details(term: dict) -> dict:
    """
    Extract detailed warning information from a term.
    
    Args:
        term: Term dictionary from vigilance API
        
    Returns:
        Dictionary with extracted details
    """
    details = {
        'qualification': '',
        'situation': '',
        'evolution': '',
        'observations': '',
        'recommendations': ''
    }
    
    subdivision_text = term.get('subdivision_text', [])
    
    for subdiv in subdivision_text:
        bold_text = subdiv.get('bold_text', '').lower()
        text_content = subdiv.get('text', [])
        text_combined = ' '.join(text_content)
        
        if 'qualification' in bold_text:
            details['qualification'] = text_combined
        elif 'situation' in bold_text:
            details['situation'] = text_combined
        elif 'évolution' in bold_text or 'evolution' in bold_text:
            details['evolution'] = text_combined
        elif 'observations' in bold_text:
            details['observations'] = text_combined
        elif 'recommandations' in bold_text or 'conseils' in bold_text:
            details['recommendations'] = text_combined
        elif 'faits nouveaux' in bold_text:
            details['situation'] = text_combined  # Often contains current situation
    
    return details

def _translate_warning_to_german(details: dict, risk_name: str) -> str:
    """
    Translate French warning details to German summary.
    
    Args:
        details: Warning details dictionary
        risk_name: Risk level name
        
    Returns:
        German summary string
    """
    # Comprehensive French to German hazard translations
    hazard_translations = {
        # Heat-related
        'canicule': 'Hitzewelle',
        'chaleur': 'Hitze',
        'forte chaleur': 'starke Hitze',
        'pic caniculaire': 'Hitzespitze',
        
        # Storms and thunderstorms
        'orages': 'Gewitter',
        'orage': 'Gewitter',
        'orage violent': 'heftiges Gewitter',
        'orageux': 'gewittrig',
        'pluvio-orageux': 'regen-gewittrig',
        
        # Rain and precipitation
        'pluie': 'Regen',
        'pluies': 'Regen',
        'pluie forte': 'starker Regen',
        'pluies intenses': 'intensive Regenfälle',
        'précipitations': 'Niederschlag',
        
        # Wind
        'vent': 'Wind',
        'vents': 'Wind',
        'vent fort': 'starker Wind',
        'vent violent': 'heftiger Wind',
        'rafales': 'Böen',
        
        # Snow and ice
        'neige': 'Schnee',
        'neiges': 'Schnee',
        'neige abondante': 'reichlich Schnee',
        'gel': 'Frost',
        'gèle': 'Frost',
        'verglas': 'Glatteis',
        'glace': 'Eis',
        
        # Flooding and water
        'inondation': 'Überschwemmung',
        'inondations': 'Überschwemmung',
        'crue': 'Hochwasser',
        'crues': 'Hochwasser',
        'submersion': 'Überflutung',
        'submersions': 'Überflutung',
        'vague': 'Welle',
        'vagues': 'Wellen',
        
        # Storms and cyclones
        'tempête': 'Sturm',
        'tempêtes': 'Stürme',
        'cyclone': 'Zyklon',
        'cyclones': 'Zyklone',
        'ouragan': 'Hurrikan',
        
        # Other weather phenomena
        'brouillard': 'Nebel',
        'brouillards': 'Nebel',
        'brouillard dense': 'dichter Nebel',
        'sécheresse': 'Dürre',
        'sécheresses': 'Dürren',
        'froid': 'Kälte',
        'grand froid': 'große Kälte',
        'avalanche': 'Lawine',
        'avalanches': 'Lawinen',
        
        # Time-related
        'épisode': 'Episode',
        'durable': 'anhaltend',
        'exceptionnel': 'außergewöhnlich',
        'remarquable': 'bemerkenswert',
        'précocité': 'Frühzeitigkeit'
    }
    
    # Extract key information
    qualification = details.get('qualification', '').lower()
    situation = details.get('situation', '').lower()
    evolution = details.get('evolution', '').lower()
    observations = details.get('observations', '').lower()
    
    # Combine all text for analysis
    all_text = f"{qualification} {situation} {evolution} {observations}"
    
    # Determine hazard type and severity
    detected_hazards = []
    severity_indicators = []
    
    for french, german in hazard_translations.items():
        if french in all_text:
            if french in ['canicule', 'chaleur', 'forte chaleur', 'pic caniculaire']:
                detected_hazards.append('Hitzewelle')
            elif french in ['orages', 'orage', 'orage violent', 'orageux']:
                detected_hazards.append('Gewitter')
            elif french in ['pluie', 'pluies', 'pluie forte', 'pluies intenses']:
                detected_hazards.append('Starkregen')
            elif french in ['vent', 'vents', 'vent fort', 'vent violent', 'rafales']:
                detected_hazards.append('Sturm')
            elif french in ['neige', 'neiges', 'neige abondante']:
                detected_hazards.append('Schnee')
            elif french in ['inondation', 'inondations', 'crue', 'crues']:
                detected_hazards.append('Überschwemmung')
            elif french in ['brouillard', 'brouillards', 'brouillard dense']:
                detected_hazards.append('Nebel')
            elif french in ['gel', 'gèle', 'verglas']:
                detected_hazards.append('Frost/Glatteis')
            elif french in ['tempête', 'tempêtes', 'cyclone', 'cyclones']:
                detected_hazards.append('Sturm/Zyklon')
            elif french in ['sécheresse', 'sécheresses']:
                detected_hazards.append('Dürre')
            elif french in ['avalanche', 'avalanches']:
                detected_hazards.append('Lawine')
            
            # Check for severity indicators
            if french in ['exceptionnel', 'violent', 'forte', 'intenses', 'abondante']:
                severity_indicators.append('stark')
            if french in ['durable', 'épisode']:
                severity_indicators.append('anhaltend')
            if french in ['précocité', 'remarquable']:
                severity_indicators.append('frühzeitig')
    
    # Remove duplicates and create summary
    detected_hazards = list(set(detected_hazards))
    
    if not detected_hazards:
        # Fallback: try to determine from context
        if any(word in all_text for word in ['température', 'thermomètre', 'chaud']):
            detected_hazards.append('Hitze')
        elif any(word in all_text for word in ['précipitation', 'pluie']):
            detected_hazards.append('Regen')
        else:
            detected_hazards.append('Wetterwarnung')
    
    # Create German summary
    summary_parts = []
    
    # Add main hazard
    if len(detected_hazards) == 1:
        summary_parts.append(detected_hazards[0])
    else:
        summary_parts.append(' + '.join(detected_hazards))
    
    # Add severity indicators
    if 'stark' in severity_indicators:
        summary_parts.append("stark")
    if 'anhaltend' in severity_indicators:
        summary_parts.append("anhaltend")
    if 'frühzeitig' in severity_indicators:
        summary_parts.append("(frühzeitig)")
    
    # Add time info
    if 'demain' in evolution:
        summary_parts.append("(auch morgen)")
    
    return f"{risk_name}-Warnung: {' '.join(summary_parts)}"

def _is_warning_active(start_time: str, end_time: str) -> bool:
    """
    Check if a warning is currently active.
    
    Args:
        start_time: Warning start time (ISO format)
        end_time: Warning end time (ISO format)
        
    Returns:
        True if warning is currently active
    """
    try:
        now = datetime.now(timezone.utc)
        
        if start_time:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start = datetime.min.replace(tzinfo=timezone.utc)
            
        if end_time:
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end = datetime.max.replace(tzinfo=timezone.utc)
            
        return start <= now <= end
    except Exception as e:
        print(f"Warning: Error checking warning time: {e}")
        return False

def _generate_warning_summary(warnings: list) -> str:
    """
    Generate a human-readable summary of warnings.
    
    Args:
        warnings: List of warning dictionaries
        
    Returns:
        Summary string
    """
    if not warnings:
        return "Keine aktiven Wetterwarnungen"
    
    active_warnings = [w for w in warnings if w['is_active']]
    
    if not active_warnings:
        return "Keine aktiven Wetterwarnungen"
    
    # Group by risk level
    risk_groups = {}
    for warning in active_warnings:
        risk_level = warning['risk_level']
        if risk_level not in risk_groups:
            risk_groups[risk_level] = []
        risk_groups[risk_level].append(warning)
    
    summary_parts = []
    
    for risk_level in sorted(risk_groups.keys(), reverse=True):
        risk_name = {2: 'Gelb', 3: 'Orange', 4: 'Rot'}.get(risk_level, f'Level {risk_level}')
        count = len(risk_groups[risk_level])
        summary_parts.append(f"{count} {risk_name}-Warnung{'en' if count > 1 else ''}")
    
    return f"Aktive Warnungen: {', '.join(summary_parts)}"

def get_vigilance_summary() -> dict:
    """
    Get a comprehensive summary of current vigilance warnings.
    
    Returns:
        Structured vigilance summary
    """
    vigilance_data = fetch_vigilance_text_warnings()
    return parse_vigilance_warnings(vigilance_data)
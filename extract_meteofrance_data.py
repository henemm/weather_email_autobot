#!/usr/bin/env python3
"""
Extract weather data from Météo-France website for comparison with our system.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_meteofrance_data(url):
    """
    Extract weather data from Météo-France website.
    
    Args:
        url: Météo-France URL for specific location
        
    Returns:
        Dictionary with extracted weather data
    """
    try:
        logger.info(f"Fetching data from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract location name
        location_name = None
        title_elem = soup.find('h1')
        if title_elem:
            location_name = title_elem.get_text().strip()
            location_name = re.sub(r'METEO\s+', '', location_name)
        
        # Extract current temperature
        current_temp = None
        temp_elements = soup.find_all(text=re.compile(r'\d+°'))
        if temp_elements:
            for elem in temp_elements:
                temp_match = re.search(r'(\d+)°', elem)
                if temp_match:
                    current_temp = int(temp_match.group(1))
                    break
        
        # Extract forecast text
        forecast_text = ""
        forecast_elements = soup.find_all(text=re.compile(r'Cet après-midi|Demain|aujourd\'hui', re.IGNORECASE))
        for elem in forecast_elements:
            if len(elem.strip()) > 50:  # Only longer text blocks
                forecast_text += elem.strip() + " "
        
        # Extract specific weather conditions
        conditions = {
            'rain': False,
            'thunderstorm': False,
            'wind': False,
            'high_temp': False,
            'low_temp': False
        }
        
        forecast_lower = forecast_text.lower()
        
        # Check for rain
        if any(word in forecast_lower for word in ['pluie', 'averses', 'gouttes', 'précipitations']):
            conditions['rain'] = True
        
        # Check for thunderstorms
        if any(word in forecast_lower for word in ['orage', 'orages', 'orageux', 'orageuse']):
            conditions['thunderstorm'] = True
        
        # Check for wind
        if any(word in forecast_lower for word in ['vent', 'rafales', 'mistral', 'tramontane']):
            conditions['wind'] = True
        
        # Check for high temperatures
        if any(word in forecast_lower for word in ['chaud', 'élevées', '30', '35', '40']):
            conditions['high_temp'] = True
        
        # Check for low temperatures
        if any(word in forecast_lower for word in ['froid', 'fraîches', '10', '15']):
            conditions['low_temp'] = True
        
        # Extract temperature ranges
        temp_ranges = []
        temp_pattern = r'(\d+)\s*à\s*(\d+)\s*degrés'
        temp_matches = re.findall(temp_pattern, forecast_text)
        for match in temp_matches:
            temp_ranges.append((int(match[0]), int(match[1])))
        
        # Extract wind speeds
        wind_speeds = []
        wind_pattern = r'(\d+)\s*à\s*(\d+)\s*km/h'
        wind_matches = re.findall(wind_pattern, forecast_text)
        for match in wind_matches:
            wind_speeds.append((int(match[0]), int(match[1])))
        
        result = {
            'location': location_name,
            'url': url,
            'extracted_at': datetime.now().isoformat(),
            'current_temperature': current_temp,
            'forecast_text': forecast_text.strip(),
            'conditions': conditions,
            'temperature_ranges': temp_ranges,
            'wind_speeds': wind_speeds
        }
        
        logger.info(f"Successfully extracted data for {location_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error extracting data from {url}: {e}")
        return None

def main():
    """Main function to extract and display Météo-France data."""
    
    # Prunelli-di-Fiumorbo URL (Corsica - expected thunderstorms and rain)
    url = "https://meteofrance.com/previsions-meteo-france/prunelli-di-fiumorbo/20243"
    
    print("🌤️ MÉTÉO-FRANCE DATA EXTRACTION")
    print("=" * 50)
    
    data = extract_meteofrance_data(url)
    
    if data:
        print(f"📍 Location: {data['location']}")
        print(f"🌡️ Current Temperature: {data['current_temperature']}°C" if data['current_temperature'] else "🌡️ Current Temperature: Not found")
        print()
        
        print("📋 Weather Conditions Detected:")
        for condition, detected in data['conditions'].items():
            status = "✅" if detected else "❌"
            print(f"  {status} {condition.replace('_', ' ').title()}")
        
        print()
        print("🌡️ Temperature Ranges:")
        if data['temperature_ranges']:
            for min_temp, max_temp in data['temperature_ranges']:
                print(f"  {min_temp}°C to {max_temp}°C")
        else:
            print("  No temperature ranges found")
        
        print()
        print("💨 Wind Speeds:")
        if data['wind_speeds']:
            for min_wind, max_wind in data['wind_speeds']:
                print(f"  {min_wind} to {max_wind} km/h")
        else:
            print("  No wind speeds found")
        
        print()
        print("📝 Full Forecast Text:")
        print(f"  {data['forecast_text'][:200]}...")
        
        print()
        print("💾 Data saved to meteofrance_extracted_data.json")
        
        # Save to file
        with open('meteofrance_extracted_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    else:
        print("❌ Failed to extract data from Météo-France website")

if __name__ == "__main__":
    main() 
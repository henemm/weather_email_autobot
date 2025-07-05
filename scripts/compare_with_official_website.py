#!/usr/bin/env python3
"""
Compare Météo-France API results with official website data.
This helps identify and fix problems in the API query code.
"""

import sys
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meteofrance_api.client import MeteoFranceClient


def fetch_official_website_data() -> Dict[str, Any]:
    """
    Fetch weather data from the official Météo-France website for Haute-Corse.
    
    Returns:
        Dictionary with weather data from the website
    """
    print("🌐 FETCHING OFFICIAL MÉTÉO-FRANCE WEBSITE DATA")
    print("=" * 60)
    
    # URL for Haute-Corse weather
    url = "https://meteofrance.com/previsions-meteo-france/haute-corse/2b"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Website response status: {response.status_code}")
        print(f"✅ Content length: {len(response.text)} characters")
        
        # Save the raw HTML for analysis
        output_file = "output/debug/official_website_raw.html"
        Path("output/debug").mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"💾 Raw HTML saved to: {output_file}")
        
        # Extract weather information from the HTML
        weather_data = extract_weather_from_html(response.text)
        
        return weather_data
        
    except Exception as e:
        print(f"❌ Error fetching website data: {e}")
        return {}


def extract_weather_from_html(html_content: str) -> Dict[str, Any]:
    """
    Extract weather information from Météo-France HTML content.
    
    Args:
        html_content: Raw HTML from the website
        
    Returns:
        Dictionary with extracted weather data
    """
    print("\n🔍 EXTRACTING WEATHER DATA FROM HTML")
    print("-" * 40)
    
    weather_data = {
        'extraction_time': datetime.now().isoformat(),
        'source': 'meteofrance.com',
        'region': 'Haute-Corse (2B)',
        'weather_conditions': [],
        'alerts': [],
        'forecast_summary': ''
    }
    
    try:
        # Look for weather condition keywords in the HTML
        weather_keywords = [
            'orage', 'orages', 'thunderstorm', 'storm',
            'averse', 'averses', 'shower', 'showers',
            'pluie', 'pluies', 'rain', 'rains',
            'ensoleillé', 'sunny', 'clear',
            'nuageux', 'cloudy', 'overcast'
        ]
        
        html_lower = html_content.lower()
        
        print("🔍 Searching for weather conditions...")
        for keyword in weather_keywords:
            if keyword in html_lower:
                # Find context around the keyword
                start = max(0, html_lower.find(keyword) - 50)
                end = min(len(html_lower), html_lower.find(keyword) + 100)
                context = html_content[start:end].replace('\n', ' ').strip()
                
                weather_data['weather_conditions'].append({
                    'keyword': keyword,
                    'context': context
                })
                print(f"  Found '{keyword}' in context: {context[:100]}...")
        
        # Look for alert information
        alert_keywords = ['vigilance', 'alerte', 'warning', 'orange', 'rouge', 'jaune']
        for keyword in alert_keywords:
            if keyword in html_lower:
                start = max(0, html_lower.find(keyword) - 30)
                end = min(len(html_lower), html_lower.find(keyword) + 100)
                context = html_content[start:end].replace('\n', ' ').strip()
                
                weather_data['alerts'].append({
                    'keyword': keyword,
                    'context': context
                })
                print(f"  Found alert '{keyword}' in context: {context[:100]}...")
        
        # Extract forecast summary if available
        if 'tendance' in html_lower or 'prévision' in html_lower:
            # Look for forecast text
            forecast_markers = ['tendance pour les jours suivants', 'prévisions', 'météo']
            for marker in forecast_markers:
                if marker in html_lower:
                    start = html_lower.find(marker)
                    end = min(len(html_lower), start + 500)
                    forecast_text = html_content[start:end].replace('\n', ' ').strip()
                    weather_data['forecast_summary'] = forecast_text
                    print(f"  Found forecast summary: {forecast_text[:200]}...")
                    break
        
        print(f"✅ Extracted {len(weather_data['weather_conditions'])} weather conditions")
        print(f"✅ Extracted {len(weather_data['alerts'])} alerts")
        
        return weather_data
        
    except Exception as e:
        print(f"❌ Error extracting weather data: {e}")
        return weather_data


def compare_api_with_website():
    """
    Compare API results with official website data.
    """
    print("🔍 COMPARING API WITH OFFICIAL WEBSITE")
    print("=" * 60)
    
    # Test coordinates (Asco)
    latitude = 42.426238
    longitude = 8.900291
    
    print(f"Testing coordinates: {latitude}, {longitude}")
    print()
    
    # Get website data
    website_data = fetch_official_website_data()
    
    if not website_data:
        print("❌ Could not fetch website data")
        return
    
    # Get API data
    print("\n📡 FETCHING API DATA")
    print("-" * 40)
    
    try:
        client = MeteoFranceClient()
        forecast = client.get_forecast(latitude, longitude)
        
        print(f"✅ API call successful!")
        print(f"✅ Number of forecast entries: {len(forecast.forecast)}")
        
        # Find entries for today (14-17 Uhr)
        today_entries = []
        for i, entry in enumerate(forecast.forecast):
            dt_timestamp = entry.get('dt')
            if dt_timestamp:
                entry_datetime = datetime.fromtimestamp(dt_timestamp)
                today = datetime.now().date()
                
                if entry_datetime.date() == today and 14 <= entry_datetime.hour <= 17:
                    today_entries.append({
                        'index': i,
                        'datetime': entry_datetime,
                        'entry': entry
                    })
        
        print(f"✅ Found {len(today_entries)} entries for today 14-17 Uhr")
        
        # Compare website vs API
        print("\n📊 COMPARISON: WEBSITE vs API")
        print("-" * 40)
        
        print("🌐 WEBSITE DATA:")
        print(f"  Region: {website_data['region']}")
        print(f"  Weather conditions found: {len(website_data['weather_conditions'])}")
        for condition in website_data['weather_conditions'][:3]:  # Show first 3
            print(f"    - {condition['keyword']}: {condition['context'][:80]}...")
        
        print(f"  Alerts found: {len(website_data['alerts'])}")
        for alert in website_data['alerts'][:3]:  # Show first 3
            print(f"    - {alert['keyword']}: {alert['context'][:80]}...")
        
        print("\n📡 API DATA:")
        for entry in today_entries:
            dt = entry['datetime']
            weather = entry['entry'].get('weather', {})
            weather_desc = weather.get('desc', 'Unknown') if isinstance(weather, dict) else str(weather)
            
            print(f"  {dt.strftime('%H:%M')}: {weather_desc}")
        
        # Look for discrepancies
        print("\n🔍 ANALYZING DISCREPANCIES")
        print("-" * 40)
        
        # Check if website mentions thunderstorms but API doesn't
        website_has_thunderstorm = any(
            'orage' in condition['keyword'] or 'orage' in condition['context'].lower()
            for condition in website_data['weather_conditions']
        )
        
        api_has_thunderstorm = any(
            'orage' in entry['entry'].get('weather', {}).get('desc', '').lower()
            for entry in today_entries
        )
        
        print(f"Website mentions thunderstorms: {website_has_thunderstorm}")
        print(f"API mentions thunderstorms: {api_has_thunderstorm}")
        
        if website_has_thunderstorm and not api_has_thunderstorm:
            print("❌ DISCREPANCY: Website mentions thunderstorms but API doesn't!")
            print("   This indicates a problem with the API query or data processing.")
        elif not website_has_thunderstorm and api_has_thunderstorm:
            print("❌ DISCREPANCY: API mentions thunderstorms but website doesn't!")
        else:
            print("✅ CONSISTENT: Both website and API show similar thunderstorm data")
        
        # Save comparison results
        comparison_data = {
            'timestamp': datetime.now().isoformat(),
            'coordinates': {'lat': latitude, 'lon': longitude},
            'website_data': website_data,
            'api_entries': [
                {
                    'index': entry['index'],
                    'datetime': entry['datetime'].isoformat(),
                    'weather': entry['entry'].get('weather', {}),
                    'temperature': entry['entry'].get('T', {}),
                    'rain': entry['entry'].get('rain', {}),
                    'wind': entry['entry'].get('wind', {})
                }
                for entry in today_entries
            ],
            'discrepancies': {
                'website_has_thunderstorm': website_has_thunderstorm,
                'api_has_thunderstorm': api_has_thunderstorm,
                'consistent': website_has_thunderstorm == api_has_thunderstorm
            }
        }
        
        output_file = "output/debug/website_api_comparison.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, indent=2, default=str)
        
        print(f"\n💾 Comparison data saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error comparing data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    compare_api_with_website() 
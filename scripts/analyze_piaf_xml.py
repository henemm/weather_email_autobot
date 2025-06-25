#!/usr/bin/env python3
"""
Script to analyze PIAF XML response and extract bounding box information.
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

def fetch_piaf_capabilities() -> str:
    """Fetch PIAF capabilities XML."""
    url = 'https://api.meteofrance.fr/pro/piaf/1.0/wcs/MF-NWP-HIGHRES-PIAF-001-FRANCE-WCS/GetCapabilities?service=WCS&version=2.0.1&language=eng'
    
    # Use the token from the curl example
    token = "eyJ4NXQiOiJOelU0WTJJME9XRXhZVGt6WkdJM1kySTFaakZqWVRJeE4yUTNNalEyTkRRM09HRmtZalkzTURkbE9UZ3paakUxTURRNFltSTVPR1kyTURjMVkyWTBNdyIsImtpZCI6Ik56VTRZMkkwT1dFeFlUa3paR0kzWTJJMVpqRmpZVEl4TjJRM01qUTJORFEzT0dGa1lqWTNNRGRsT1RnelpqRTFNRFE0WW1JNU9HWTJNRGMxWTJZME13X1JTMjU2IiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMjA1NzVjZi1kOGQzLTRmOWQtOWU1NC1jOTg0MWIxZTZmZmYiLCJhdXQiOiJBUFBMSUNBVElPTiIsImF1ZCI6Imx4aEQ2Q25HMjlicUNZWUNRX295T2E5UDlYQWEiLCJuYmYiOjE3NTA2MjMyODUsImF6cCI6Imx4aEQ2Q25HMjlicUNZWUNRX295T2E5UDlYQWEiLCJzY29wZSI6ImRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnJcL29hdXRoMlwvdG9rZW4iLCJleHAiOjE3NTA2MjY4ODUsImlhdCI6MTc1MDYyMzI4NSwianRpIjoiMWZmODdjOTMtNTU5My00ZTdhLTlmODctZDliMzVlMWJkZWNmIiwiY2xpZW50X2lkIjoibHhoRDZDbkcyOWJxQ1lZQ1Ffb3lPYTlQOVhBYSJ9.CXSgG4lBYtn3C-d6kPpqDryc7z3-YYGMJwrVp53Dhi8FHhi3wWBfP_NBLR8fCwP4ZKZJdZ1HlWpiNAcDaifiMKCsff9WzS06y1P6-tv4fRpshdSKx4mn1BGdWb36GGWsIbek13S_zaui9SKYbCHsvb6sYt826o4_X4_9E3NoPhyFAl7r2tygZ83GZjBHuU1rpqQ31k6uZO1ZwOHB2GK7TBOW7co8LsAkl80zjuOwcm2oYkyRNTp3v5OB-FmHlbHYRRRJViS_3uV0nM-Cn1QnxQpcU-o91ijT68SKrcd088_GPm7_du5zbvZIqz9ve5bEe6r1LTQrP5CkcDaAyDoWDA"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
    
    return response.text

def analyze_piaf_xml(xml_content: str) -> Dict[str, Any]:
    """Analyze PIAF XML and extract bounding box information."""
    
    # Register namespaces
    namespaces = {
        'wcs': 'http://www.opengis.net/wcs/2.0',
        'ows': 'http://www.opengis.net/ows/2.0',
        'gml': 'http://www.opengis.net/gml/3.2'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        print("=== PIAF XML Analysis ===\n")
        
        # Look for service identification
        service_id = root.find('.//ows:ServiceIdentification', namespaces)
        if service_id is not None:
            title = service_id.find('ows:Title', namespaces)
            if title is not None:
                print(f"Service Title: {title.text}")
        
        # Look for bounding box information in different locations
        print("\n🔍 Searching for Bounding Box Information:")
        
        # 1. Check for WGS84BoundingBox in CoverageSummary
        coverage_summaries = root.findall('.//wcs:CoverageSummary', namespaces)
        print(f"Found {len(coverage_summaries)} CoverageSummary elements")
        
        for i, coverage in enumerate(coverage_summaries[:3]):  # Check first 3
            print(f"\nCoverage {i+1}:")
            
            # Check for CoverageId
            coverage_id = coverage.find('wcs:CoverageId', namespaces)
            if coverage_id is not None:
                print(f"  ID: {coverage_id.text}")
            
            # Check for WGS84BoundingBox
            bbox = coverage.find('.//wcs:WGS84BoundingBox', namespaces)
            if bbox is not None:
                print("  ✅ Found WGS84BoundingBox!")
                lower_corner = bbox.find('ows:LowerCorner', namespaces)
                upper_corner = bbox.find('ows:UpperCorner', namespaces)
                if lower_corner is not None and upper_corner is not None:
                    print(f"    Lower Corner: {lower_corner.text}")
                    print(f"    Upper Corner: {upper_corner.text}")
            else:
                print("  ❌ No WGS84BoundingBox found")
            
            # Check for other bounding box types
            other_bbox = coverage.find('.//gml:Envelope', namespaces)
            if other_bbox is not None:
                print("  ✅ Found gml:Envelope!")
                print(f"    Envelope: {other_bbox.attrib}")
        
        # 2. Check for global bounding box in service metadata
        print("\n🔍 Checking Service-Level Bounding Box:")
        service_bbox = root.find('.//ows:WGS84BoundingBox', namespaces)
        if service_bbox is not None:
            print("✅ Found service-level WGS84BoundingBox!")
            lower_corner = service_bbox.find('ows:LowerCorner', namespaces)
            upper_corner = service_bbox.find('ows:UpperCorner', namespaces)
            if lower_corner is not None and upper_corner is not None:
                print(f"  Lower Corner: {lower_corner.text}")
                print(f"  Upper Corner: {upper_corner.text}")
        else:
            print("❌ No service-level WGS84BoundingBox found")
        
        # 3. Check for any envelope elements
        print("\n🔍 Checking for any Envelope elements:")
        envelopes = root.findall('.//gml:Envelope', namespaces)
        print(f"Found {len(envelopes)} gml:Envelope elements")
        
        for i, envelope in enumerate(envelopes[:3]):  # Check first 3
            print(f"  Envelope {i+1}: {envelope.attrib}")
            if envelope.text:
                print(f"    Content: {envelope.text[:100]}...")
        
        # 4. Check Conca coverage based on Swagger info
        print("\n🎯 Conca Coverage Analysis (based on Swagger):")
        print("Swagger shows bbox example: 37.5,-12,55.4,16 (south,west,north,east)")
        print("Conca coordinates: 9.35°E, 41.75°N")
        
        # Parse the bbox from Swagger
        swagger_bbox = [37.5, -12, 55.4, 16]  # south, west, north, east
        conca_lon, conca_lat = 9.35, 41.75
        
        west, south, east, north = swagger_bbox[1], swagger_bbox[0], swagger_bbox[3], swagger_bbox[2]
        
        covers_conca = (west <= conca_lon <= east) and (south <= conca_lat <= north)
        
        print(f"  Bounding Box: [{west}, {south}, {east}, {north}]")
        print(f"  Conca (9.35°E, 41.75°N) covered: {'✅ YES' if covers_conca else '❌ NO'}")
        
        return {
            'swagger_bbox': swagger_bbox,
            'covers_conca': covers_conca,
            'coverage_count': len(coverage_summaries)
        }
        
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return {}

def main():
    """Main function to analyze PIAF XML."""
    try:
        print("Fetching PIAF capabilities...")
        xml_content = fetch_piaf_capabilities()
        
        print("Analyzing XML structure...")
        result = analyze_piaf_xml(xml_content)
        
        print(f"\n📊 Summary:")
        print(f"Total coverages found: {result.get('coverage_count', 0)}")
        print(f"Conca coverage: {'✅ YES' if result.get('covers_conca', False) else '❌ NO'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 
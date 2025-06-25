"""
AROME WCS Layer Analysis Module.

This module provides functionality to analyze AROME WCS/WMS capabilities
and check coverage for the Conca region (9.35°E, 41.75°N).
"""

import requests
import xml.etree.ElementTree as ET
import json
import os
from typing import List, Dict, Any, Optional
from utils.env_loader import get_env_var


def fetch_capabilities(url: str, token: str) -> str:
    """
    Fetch GetCapabilities XML from a WMS/WCS endpoint.
    
    Args:
        url: GetCapabilities URL
        token: Bearer token for authentication
        
    Returns:
        XML content as string
        
    Raises:
        RuntimeError: If request fails
    """
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            raise RuntimeError(f"Authentication failed (HTTP 401) - Token may be expired or invalid for URL: {url}")
        elif response.status_code == 404:
            raise RuntimeError(f"Service not found (HTTP 404) - Endpoint may be incorrect or service unavailable: {url}")
        elif response.status_code == 403:
            raise RuntimeError(f"Access forbidden (HTTP 403) - Token may not have permission for this service: {url}")
        else:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]} for URL: {url}")
            
    except requests.Timeout:
        raise RuntimeError(f"Request timeout for URL: {url}")
    except requests.ConnectionError:
        raise RuntimeError(f"Connection error for URL: {url}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching capabilities from {url}: {str(e)}")


def parse_wms_capabilities(xml_content: str) -> List[Dict[str, Any]]:
    """
    Parse WMS GetCapabilities XML and extract layer information.
    
    Args:
        xml_content: XML content from WMS GetCapabilities
        
    Returns:
        List of layer dictionaries with id, title, bbox, time_range
    """
    layers = []
    
    # Register namespaces
    namespaces = {
        'wms': 'http://www.opengis.net/wms',
        'ows': 'http://www.opengis.net/ows/1.1'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # Find all Layer elements that have a Name (actual layers, not container layers)
        for layer_elem in root.findall('.//wms:Layer', namespaces):
            # Only process layers that have a Name element (actual data layers)
            name_elem = layer_elem.find('wms:Name', namespaces)
            if name_elem is None:
                continue
                
            layer_info = {}
            
            # Extract layer ID
            layer_info['id'] = name_elem.text
            
            # Extract title
            title_elem = layer_elem.find('wms:Title', namespaces)
            if title_elem is not None:
                layer_info['title'] = title_elem.text
            
            # Extract abstract
            abstract_elem = layer_elem.find('wms:Abstract', namespaces)
            if abstract_elem is not None:
                layer_info['abstract'] = abstract_elem.text
            
            # Extract bounding box (always use namespace for test XML)
            bbox_elem = layer_elem.find('wms:EX_GeographicBoundingBox', namespaces)
            if bbox_elem is not None:
                def get_text_ns(tag):
                    el = bbox_elem.find(f'wms:{tag}', namespaces)
                    if el is not None:
                        return el.text
                    return None
                west = get_text_ns('westBoundLongitude')
                east = get_text_ns('eastBoundLongitude')
                south = get_text_ns('southBoundLatitude')
                north = get_text_ns('northBoundLatitude')
                if None not in (west, east, south, north):
                    layer_info['bbox'] = [float(west), float(south), float(east), float(north)]
            
            # Extract time dimension
            time_elem = layer_elem.find('.//wms:Dimension[@name="time"]', namespaces)
            if time_elem is not None:
                layer_info['time_range'] = time_elem.text
            
            layers.append(layer_info)
                
    except ET.ParseError as e:
        print(f"Warning: Could not parse WMS XML: {e}")
    
    return layers


def parse_wcs_capabilities(xml_content: str) -> List[Dict[str, Any]]:
    """
    Parse WCS GetCapabilities XML and extract coverage information.
    
    Args:
        xml_content: XML content from WCS GetCapabilities
        
    Returns:
        List of coverage dictionaries with id, bbox, time_range
    """
    coverages = []
    
    # Register namespaces
    namespaces = {
        'wcs': 'http://www.opengis.net/wcs/2.0',
        'ows': 'http://www.opengis.net/ows/1.1'
    }
    
    try:
        root = ET.fromstring(xml_content)
        
        # Find all CoverageSummary elements
        for coverage_elem in root.findall('.//wcs:CoverageSummary', namespaces):
            coverage_info = {}
            
            # Extract coverage ID
            id_elem = coverage_elem.find('wcs:CoverageId', namespaces)
            if id_elem is not None:
                coverage_info['id'] = id_elem.text
            
            # Extract coverage subtype
            subtype_elem = coverage_elem.find('wcs:CoverageSubtype', namespaces)
            if subtype_elem is not None:
                coverage_info['subtype'] = subtype_elem.text
            
            # Extract WGS84 bounding box (preferred for geographic coordinates)
            bbox_elem = coverage_elem.find('.//wcs:WGS84BoundingBox', namespaces)
            if bbox_elem is not None:
                lower_corner = bbox_elem.find('ows:LowerCorner', namespaces).text.split()
                upper_corner = bbox_elem.find('ows:UpperCorner', namespaces).text.split()
                
                west = float(lower_corner[0])
                south = float(lower_corner[1])
                east = float(upper_corner[0])
                north = float(upper_corner[1])
                
                coverage_info['bbox'] = [west, south, east, north]
            else:
                # Fallback: Use known bounding box for all AROME services
                # Based on Swagger documentation: 37.5,-12,55.4,16 (south,west,north,east)
                # Convert to [west, south, east, north] format
                coverage_info['bbox'] = [-12.0, 37.5, 16.0, 55.4]
                coverage_info['bbox_source'] = 'swagger_documentation'
            
            # Extract time dimension if available
            time_elem = coverage_elem.find('.//wcs:Dimension[@name="time"]', namespaces)
            if time_elem is not None:
                coverage_info['time_range'] = time_elem.text
            
            if coverage_info:  # Only add if we have some information
                coverages.append(coverage_info)
                
    except ET.ParseError as e:
        print(f"Warning: Could not parse WCS XML: {e}")
    
    return coverages


def check_conca_coverage(bbox: List[float]) -> bool:
    """
    Check if the Conca region (9.35°E, 41.75°N) is covered by the bounding box.
    
    Args:
        bbox: Bounding box as [west, south, east, north]
        
    Returns:
        True if Conca is covered, False otherwise
    """
    conca_lon, conca_lat = 9.35, 41.75
    west, south, east, north = bbox
    
    return (west <= conca_lon <= east) and (south <= conca_lat <= north)


def analyze_arome_layers() -> List[Dict[str, Any]]:
    """
    Analyze all AROME WCS/WMS endpoints and extract layer information.
    
    Returns:
        List of service analysis results with endpoint, layers, and Conca coverage
    """
    try:
        from src.auth.api_token_provider import get_api_token
    except ImportError:
        from auth.api_token_provider import get_api_token
    
    endpoints = [
        {
            'name': 'AROME Model (WMS)',
            'url': 'https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities?service=WMS&version=1.3.0&language=eng',
            'type': 'wms',
            'service': 'wms'
        },
        {
            'name': 'AROME Immediate Forecast (WCS)',
            'url': 'https://public-api.meteofrance.fr/public/aromepi/1.0/wcs/MF-NWP-HIGHRES-AROMEPI-001-FRANCE-WCS/GetCapabilities?service=WCS&version=2.0.1&language=eng',
            'type': 'wcs',
            'service': 'aromepi'
        },
        {
            'name': 'AROME Aggregated Rainrate Forecast (WCS)',
            'url': 'https://public-api.meteofrance.fr/public/arome-agg/1.0/wcs/MF-NWP-HIGHRES-AROME-AGG-001-FRANCE-WCS?service=WCS&version=2.0.1&request=GetCapabilities',
            'type': 'wcs',
            'service': 'wcs'
        },
        {
            'name': 'AROME Model Merged Aggregated Immediate Forecast (PIAF)',
            'url': 'https://api.meteofrance.fr/pro/piaf/1.0/wcs/MF-NWP-HIGHRES-PIAF-001-FRANCE-WCS/GetCapabilities?service=WCS&version=2.0.1&language=eng',
            'type': 'wcs',
            'service': 'piaf'
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            # Get API-specific token
            token = get_api_token(endpoint['service'])
            
            # Fetch capabilities
            if endpoint['type'] == 'wms':
                layers = parse_wms_capabilities(fetch_capabilities(endpoint['url'], token))
            else:
                layers = parse_wcs_capabilities(fetch_capabilities(endpoint['url'], token))
            
            # Check Conca coverage for all layers
            conca_coverage = check_conca_coverage(layers)
            
            result = {
                'endpoint': endpoint['name'],
                'url': endpoint['url'],
                'type': endpoint['type'],
                'layers_found': len(layers),
                'conca_coverage': conca_coverage,
                'layers': layers[:10] if layers else [],  # First 10 layers as sample
                'status': 'success'
            }
            
        except Exception as e:
            result = {
                'endpoint': endpoint['name'],
                'url': endpoint['url'],
                'type': endpoint['type'],
                'error': str(e),
                'status': 'error'
            }
        
        results.append(result)
    
    return results


def save_analysis_results(results: List[Dict[str, Any]], output_file: str = "output/analyzed_arome_layers.json") -> None:
    """
    Save analysis results to JSON file.
    
    Args:
        results: Analysis results from analyze_arome_layers()
        output_file: Output file path
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis results saved to {output_file}")


def main():
    """Main function to run the AROME layer analysis."""
    print("Starting AROME WCS/WMS Layer Analysis...")
    
    results = analyze_arome_layers()
    save_analysis_results(results)
    
    # Print summary
    total_layers = sum(len(service['layers']) for service in results)
    conca_covered_layers = sum(
        sum(1 for layer in service['layers'] if layer.get('covers_conca') is True)
        for service in results
    )
    
    print(f"\nAnalysis Summary:")
    print(f"Total layers found: {total_layers}")
    print(f"Layers covering Conca: {conca_covered_layers}")
    
    for service in results:
        if 'error' not in service:
            service_conca_count = sum(1 for layer in service['layers'] if layer.get('covers_conca') is True)
            print(f"  {service['name']}: {len(service['layers'])} layers, {service_conca_count} cover Conca")


if __name__ == "__main__":
    main() 
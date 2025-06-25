#!/usr/bin/env python3
"""
Demo script for AROME WCS/WMS Layer Analysis.

This script demonstrates the analysis of AROME capabilities
and checks coverage for the Conca region.
"""

import sys
import os
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from wetter.analyze_arome_layers import analyze_arome_layers, save_analysis_results


def main():
    """Run the AROME layer analysis demo."""
    print("=" * 60)
    print("AROME WCS/WMS Layer Analysis Demo")
    print("=" * 60)
    
    try:
        # Run the analysis
        results = analyze_arome_layers()
        
        # Save results
        output_file = "output/analyzed_arome_layers.json"
        save_analysis_results(results, output_file)
        
        # Display detailed results
        print("\n" + "=" * 60)
        print("DETAILED ANALYSIS RESULTS")
        print("=" * 60)
        
        for service in results:
            print(f"\n📡 {service['name']}")
            print(f"   Type: {service['type'].upper()}")
            print(f"   Endpoint: {service['endpoint']}")
            
            if 'error' in service:
                print(f"   ❌ Error: {service['error']}")
                continue
            
            print(f"   ✅ Found {len(service['layers'])} layers")
            
            # Count Conca coverage
            conca_covered = sum(1 for layer in service['layers'] if layer.get('covers_conca') is True)
            print(f"   🎯 Conca coverage: {conca_covered}/{len(service['layers'])} layers")
            
            # Show first few layers as examples
            for i, layer in enumerate(service['layers'][:3]):
                print(f"   Layer {i+1}: {layer.get('id', 'N/A')}")
                if 'title' in layer:
                    print(f"     Title: {layer['title']}")
                if 'bbox' in layer:
                    bbox = layer['bbox']
                    print(f"     BBox: [{bbox[0]:.2f}, {bbox[1]:.2f}, {bbox[2]:.2f}, {bbox[3]:.2f}]")
                print(f"     Covers Conca: {'✅' if layer.get('covers_conca') else '❌'}")
            
            if len(service['layers']) > 3:
                print(f"   ... and {len(service['layers']) - 3} more layers")
        
        # Summary statistics
        print("\n" + "=" * 60)
        print("SUMMARY STATISTICS")
        print("=" * 60)
        
        total_layers = sum(len(service['layers']) for service in results if 'error' not in service)
        total_conca_covered = sum(
            sum(1 for layer in service['layers'] if layer.get('covers_conca') is True)
            for service in results if 'error' not in service
        )
        successful_services = sum(1 for service in results if 'error' not in service)
        
        print(f"✅ Successful services: {successful_services}/{len(results)}")
        print(f"📊 Total layers analyzed: {total_layers}")
        print(f"🎯 Layers covering Conca: {total_conca_covered}")
        print(f"📈 Coverage percentage: {(total_conca_covered/total_layers*100):.1f}%" if total_layers > 0 else "N/A")
        
        print(f"\n📄 Full results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
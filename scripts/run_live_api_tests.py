#!/usr/bin/env python3
"""
Live API Test Runner for GR20 Weather System.

This script runs the comprehensive live API tests and generates a detailed report
following the test plan from tests/manual/live_api_tests.md.
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Fix import path for env_loader
try:
    from utils.env_loader import get_env_var
except ImportError:
    try:
        from src.utils.env_loader import get_env_var
    except ImportError:
        # Add current directory to path for direct execution
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.utils.env_loader import get_env_var


def check_environment_setup() -> Dict[str, bool]:
    """
    Check if all required environment variables are set.
    
    Returns:
        Dict with environment variable status
    """
    required_vars = [
        "METEOFRANCE_CLIENT_ID",
        "METEOFRANCE_CLIENT_SECRET", 
        "GMAIL_APP_PW"
    ]
    
    optional_vars = [
        "METEOFRANCE_WCS_TOKEN",
        "METEOFRANCE_BASIC_AUTH"
    ]
    
    env_status = {}
    
    print("🔧 Environment Setup Check")
    print("=" * 50)
    
    # Check required variables
    print("\nRequired Environment Variables:")
    for var in required_vars:
        value = get_env_var(var)
        if value:
            env_status[var] = True
            print(f"✅ {var}: Set")
        else:
            env_status[var] = False
            print(f"❌ {var}: Not set")
    
    # Check optional variables
    print("\nOptional Environment Variables:")
    for var in optional_vars:
        value = get_env_var(var)
        if value:
            env_status[var] = True
            print(f"✅ {var}: Set")
        else:
            env_status[var] = False
            print(f"⚠️ {var}: Not set (some tests may be skipped)")
    
    return env_status


def run_individual_api_tests() -> Dict[str, Any]:
    """
    Run individual API tests (7 APIs).
    
    Returns:
        Dict with test results
    """
    print("\n🧪 1️⃣ Individual API Tests (7 APIs)")
    print("=" * 50)
    
    test_results = {}
    
    # Test AROME_HR
    print("\n📡 Testing AROME_HR (Temperature, CAPE, SHEAR)...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestIndividualAPIs::test_arome_hr_temperature_cape_shear",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=120)
        
        test_results["AROME_HR"] = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ AROME_HR: PASSED")
        elif "SKIPPED" in result.stdout:
            print("⚠️ AROME_HR: SKIPPED (no token)")
        else:
            print("❌ AROME_HR: FAILED")
            
    except subprocess.TimeoutExpired:
        test_results["AROME_HR"] = {
            "success": False,
            "output": "",
            "error": "Test timed out after 120 seconds",
            "skipped": False
        }
        print("⏰ AROME_HR: TIMEOUT")
    
    # Test AROME_HR_NOWCAST
    print("\n📡 Testing AROME_HR_NOWCAST (Precipitation, Visibility)...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestIndividualAPIs::test_arome_hr_nowcast_precipitation_visibility",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=120)
        
        test_results["AROME_HR_NOWCAST"] = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ AROME_HR_NOWCAST: PASSED")
        elif "SKIPPED" in result.stdout:
            print("⚠️ AROME_HR_NOWCAST: SKIPPED (no token)")
        else:
            print("❌ AROME_HR_NOWCAST: FAILED")
            
    except subprocess.TimeoutExpired:
        test_results["AROME_HR_NOWCAST"] = {
            "success": False,
            "output": "",
            "error": "Test timed out after 120 seconds",
            "skipped": False
        }
        print("⏰ AROME_HR_NOWCAST: TIMEOUT")
    
    # Test PIAF_NOWCAST
    print("\n📡 Testing PIAF_NOWCAST (Heavy Rain)...")
    try:
        piaf_result = subprocess.run([
            "python", "-m", "pytest",
            "tests/test_live_api_integration.py::TestIndividualAPIs::test_piaf_nowcast_heavy_rain",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        if piaf_result.returncode == 0:
            test_results["PIAF_NOWCAST"] = {
                "status": "PASSED",
                "output": piaf_result.stdout
            }
            print("✅ PIAF_NOWCAST: PASSED")
        else:
            test_results["PIAF_NOWCAST"] = {
                "status": "FAILED",
                "output": piaf_result.stdout + piaf_result.stderr
            }
            print("❌ PIAF_NOWCAST: FAILED")
    except subprocess.TimeoutExpired:
        test_results["PIAF_NOWCAST"] = {
            "status": "TIMEOUT",
            "output": "Test timed out after 60 seconds"
        }
        print("⏰ PIAF_NOWCAST: TIMEOUT")
    
    # Test VIGILANCE_API
    print("\n📡 Testing VIGILANCE_API (Corsica Warnings)...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestIndividualAPIs::test_vigilance_api_corsica_warnings",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=120)
        
        test_results["VIGILANCE_API"] = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ VIGILANCE_API: PASSED")
        elif "SKIPPED" in result.stdout:
            print("⚠️ VIGILANCE_API: SKIPPED (no token)")
        else:
            print("❌ VIGILANCE_API: FAILED")
            
    except subprocess.TimeoutExpired:
        test_results["VIGILANCE_API"] = {
            "success": False,
            "output": "",
            "error": "Test timed out after 120 seconds",
            "skipped": False
        }
        print("⏰ VIGILANCE_API: TIMEOUT")
    
    # Test OPENMETEO_GLOBAL
    print("\n📡 Testing OPENMETEO_GLOBAL (Temperature, Rain)...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestIndividualAPIs::test_openmeteo_global_temperature_rain",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        test_results["OPENMETEO_GLOBAL"] = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ OPENMETEO_GLOBAL: PASSED")
        else:
            print("❌ OPENMETEO_GLOBAL: FAILED")
            
    except subprocess.TimeoutExpired:
        test_results["OPENMETEO_GLOBAL"] = {
            "success": False,
            "output": "",
            "error": "Test timed out after 60 seconds",
            "skipped": False
        }
        print("⏰ OPENMETEO_GLOBAL: TIMEOUT")
    
    return test_results


def run_aggregated_weather_report_test() -> Dict[str, Any]:
    """
    Run aggregated weather report test.
    
    Returns:
        Dict with test results
    """
    print("\n🧪 2️⃣ Aggregated Weather Report Test")
    print("=" * 50)
    
    print("\n📊 Testing analyse_weather function...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestAggregatedWeatherReport::test_analyse_weather_function",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        test_result = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ Weather Analysis: PASSED")
        elif "SKIPPED" in result.stdout:
            print("⚠️ Weather Analysis: SKIPPED (no token)")
        else:
            print("❌ Weather Analysis: FAILED")
            
    except subprocess.TimeoutExpired:
        test_result = {
            "success": False,
            "output": "",
            "error": "Test timed out after 60 seconds",
            "skipped": False
        }
        print("⏰ Weather Analysis: TIMEOUT")
    
    return test_result


def run_end_to_end_test() -> Dict[str, Any]:
    """
    Run end-to-end GR20 weather report test.
    
    Returns:
        Dict with test results
    """
    print("\n🧪 3️⃣ End-to-End Test: GR20 Live Weather Report")
    print("=" * 50)
    
    print("\n🔄 Testing complete GR20 workflow...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestEndToEndGR20WeatherReport::test_gr20_live_weather_report",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=180)
        
        test_result = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ GR20 End-to-End: PASSED")
        elif "SKIPPED" in result.stdout:
            print("⚠️ GR20 End-to-End: SKIPPED (no token)")
        else:
            print("❌ GR20 End-to-End: FAILED")
            
    except subprocess.TimeoutExpired:
        test_result = {
            "success": False,
            "output": "",
            "error": "Test timed out after 180 seconds",
            "skipped": False
        }
        print("⏰ GR20 End-to-End: TIMEOUT")
    
    return test_result


def run_fallback_tests() -> Dict[str, Any]:
    """
    Run API connectivity and fallback tests.
    
    Returns:
        Dict with test results
    """
    print("\n🧪 API Connectivity and Fallback Tests")
    print("=" * 50)
    
    fallback_results = {}
    
    # Test fallback behavior
    print("\n🔄 Testing API fallback behavior...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestAPIConnectivityAndFallbacks::test_api_fallback_behavior",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        fallback_results["fallback_behavior"] = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ API Fallback: PASSED")
        else:
            print("❌ API Fallback: FAILED")
            
    except subprocess.TimeoutExpired:
        fallback_results["fallback_behavior"] = {
            "success": False,
            "output": "",
            "error": "Test timed out after 60 seconds",
            "skipped": False
        }
        print("⏰ API Fallback: TIMEOUT")
    
    # Test error handling
    print("\n🔄 Testing error handling...")
    try:
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/test_live_api_integration.py::TestAPIConnectivityAndFallbacks::test_error_handling",
            "-v", "-s", "--tb=short"
        ], capture_output=True, text=True, timeout=30)
        
        fallback_results["error_handling"] = {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": "SKIPPED" in result.stdout
        }
        
        if result.returncode == 0:
            print("✅ Error Handling: PASSED")
        else:
            print("❌ Error Handling: FAILED")
            
    except subprocess.TimeoutExpired:
        fallback_results["error_handling"] = {
            "success": False,
            "output": "",
            "error": "Test timed out after 30 seconds",
            "skipped": False
        }
        print("⏰ Error Handling: TIMEOUT")
    
    return fallback_results


def generate_test_report(
    env_status: Dict[str, bool],
    individual_results: Dict[str, Any],
    aggregated_result: Dict[str, Any],
    end_to_end_result: Dict[str, Any],
    fallback_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate comprehensive test report.
    
    Returns:
        Dict with complete test report
    """
    print("\n📊 Generating Test Report")
    print("=" * 50)
    
    # Calculate statistics
    total_individual_tests = len(individual_results)
    passed_individual_tests = sum(1 for r in individual_results.values() if r["success"])
    skipped_individual_tests = sum(1 for r in individual_results.values() if r["skipped"])
    failed_individual_tests = total_individual_tests - passed_individual_tests - skipped_individual_tests
    
    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_plan_version": "tests/manual/live_api_tests.md",
        "environment": {
            "status": env_status,
            "required_vars_set": all(env_status.get(var, False) for var in ["METEOFRANCE_CLIENT_ID", "METEOFRANCE_CLIENT_SECRET", "GMAIL_APP_PW"])
        },
        "test_results": {
            "individual_apis": {
                "summary": {
                    "total": total_individual_tests,
                    "passed": passed_individual_tests,
                    "failed": failed_individual_tests,
                    "skipped": skipped_individual_tests,
                    "success_rate": f"{(passed_individual_tests / total_individual_tests * 100):.1f}%" if total_individual_tests > 0 else "0%"
                },
                "details": individual_results
            },
            "aggregated_weather_report": aggregated_result,
            "end_to_end_gr20_report": end_to_end_result,
            "api_connectivity_fallbacks": fallback_results
        },
        "overall_status": "PASS" if (
            passed_individual_tests >= 1 and  # At least OpenMeteo should work
            aggregated_result["success"] and
            end_to_end_result["success"]
        ) else "FAIL"
    }
    
    # Print summary
    print(f"\n📈 Test Summary:")
    print(f"   Individual APIs: {passed_individual_tests}/{total_individual_tests} passed ({skipped_individual_tests} skipped)")
    print(f"   Aggregated Weather Report: {'✅ PASSED' if aggregated_result['success'] else '❌ FAILED'}")
    print(f"   End-to-End GR20 Report: {'✅ PASSED' if end_to_end_result['success'] else '❌ FAILED'}")
    print(f"   Overall Status: {report['overall_status']}")
    
    return report


def save_report(report: Dict[str, Any], output_dir: str = "output") -> str:
    """
    Save test report to file.
    
    Args:
        report: Test report dictionary
        output_dir: Output directory
        
    Returns:
        Path to saved report file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"live_api_test_report_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save report
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Test report saved to: {filepath}")
    return filepath


def main():
    """Main function to run all live API tests."""
    print("🌤️ Live API Test Runner for GR20 Weather System")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Plan: tests/manual/live_api_tests.md")
    print()
    
    try:
        # 1. Check environment setup
        env_status = check_environment_setup()
        
        # 2. Run individual API tests
        individual_results = run_individual_api_tests()
        
        # 3. Run aggregated weather report test
        aggregated_result = run_aggregated_weather_report_test()
        
        # 4. Run end-to-end test
        end_to_end_result = run_end_to_end_test()
        
        # 5. Run fallback tests
        fallback_results = run_fallback_tests()
        
        # 6. Generate and save report
        report = generate_test_report(
            env_status,
            individual_results,
            aggregated_result,
            end_to_end_result,
            fallback_results
        )
        
        report_file = save_report(report)
        
        print(f"\n✅ Live API Test Suite completed!")
        print(f"📊 Report: {report_file}")
        print(f"🎯 Overall Status: {report['overall_status']}")
        
        # Exit with appropriate code
        if report['overall_status'] == 'PASS':
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
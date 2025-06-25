#!/usr/bin/env python3
"""
Script to compare tokens from curl command with environment variables.
"""

import os
import re
from urllib.parse import unquote

def extract_token_from_curl(curl_command):
    """Extract the Bearer token from the curl command."""
    # Extract the Authorization header value
    auth_match = re.search(r"Authorization: Bearer ([^\s']+)", curl_command)
    if auth_match:
        return auth_match.group(1)
    return None

def decode_jwt_payload(token):
    """Decode the JWT payload to show token information."""
    import base64
    import json
    
    try:
        # Split the JWT token
        parts = token.split('.')
        if len(parts) != 3:
            return "Invalid JWT format"
        
        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        
        # Decode base64url
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded.decode('utf-8'))
    except Exception as e:
        return f"Error decoding JWT: {e}"

def main():
    # The curl command from the user
    curl_command = """curl -X 'GET' \
  'https://public-api.meteofrance.fr/public/aromepi/1.0/wcs/MF-NWP-HIGHRES-AROMEPI-001-FRANCE-WCS/GetCapabilities?service=WCS&version=2.0.1&language=eng' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer eyJ4NXQiOiJOelU0WTJJME9XRXhZVGt6WkdJM1kySTFaakZqWVRJeE4yUTNNalEyTkRRM09HRmtZalkzTURkbE9UZ3paakUxTURRNFltSTVPR1kyTURjMVkyWTBNdyIsImtpZCI6Ik56VTRZMkkwT1dFeFlUa3paR0kzWTJJMVpqRmpZVEl4TjJRM01qUTJORFEzT0dGa1lqWTNNRGRsT1RnelpqRTFNRFE0WW1JNU9HWTJNRGMxWTJZME13X1JTMjU2IiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMjA1NzVjZi1kOGQzLTRmOWQtOWU1NC1jOTg0MWIxZTZmZmYiLCJhdXQiOiJBUFBMSUNBVElPTiIsImF1ZCI6Imx4aEQ2Q25HMjlicUNZWUNRX295T2E5UDlYQWEiLCJuYmYiOjE3NTA2MjI5MTUsImF6cCI6Imx4aEQ2Q25HMjlicUNZWUNRX295T2E5UDlYQWEiLCJzY29wZSI6ImRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnJcL29hdXRoMlwvdG9rZW4iLCJleHAiOjE3NTA2MjY1MTUsImlhdCI6MTc1MDYyMjkxNSwianRpIjoiM2VkYjA2YzItN2VmMy00MGMyLWJlODEtMjZiODlhODBiMGU0IiwiY2xpZW50X2lkIjoibHhoRDZDbkcyOWJxQ1lZQ1Ffb3lPYTlQOVhBYSJ9.S5xVPkSzSMhtIEiMAxs2sWSnc21WNcd5lfGyNnOW3JMZnEq98VrTczCtzxKWcG6Jy48nypy_jtnX5zABWqGJVaojgktg1Z-Du02uoOzB5fbR9T5zVA3KM--dYo_diaulaTAiuecyh4O7wq_fqb0MrxgzKrh1cdYfLzZyEAPn16QNySmS6J6lnuN5VNr97Kg0GdPRc0cMGlPvIz_5bN54rFNVVnU0HwhAIgP-lTDoDUftBp0ZZGA5syTcditOQGx9CMF2isjLcW7jhOcf2Pdq4eiERijazHFu8iGo93nq3Tx_VC6hfKXZZjQzxN1nUxm5RBSetLVpTQWnKnbDFQT-ZA'"""
    
    print("=== Token Comparison Analysis ===\n")
    
    # Extract token from curl command
    curl_token = extract_token_from_curl(curl_command)
    if curl_token:
        print(f"✅ Token from curl command extracted successfully")
        print(f"   Length: {len(curl_token)} characters")
        print(f"   Starts with: {curl_token[:50]}...")
        print(f"   Ends with: ...{curl_token[-50:]}")
        
        # Decode JWT payload
        print("\n📋 JWT Payload Information:")
        payload = decode_jwt_payload(curl_token)
        if isinstance(payload, dict):
            print(f"   Subject (sub): {payload.get('sub', 'N/A')}")
            print(f"   Audience (aud): {payload.get('aud', 'N/A')}")
            print(f"   Scope: {payload.get('scope', 'N/A')}")
            print(f"   Issued at (iat): {payload.get('iat', 'N/A')}")
            print(f"   Expires at (exp): {payload.get('exp', 'N/A')}")
            print(f"   Client ID: {payload.get('client_id', 'N/A')}")
        else:
            print(f"   {payload}")
    else:
        print("❌ Could not extract token from curl command")
    
    # Check environment variables
    print("\n🔍 Environment Variables:")
    env_vars = [
        'METEOFRANCE_WCS_TOKEN',
        'METEOFRANCE_IFC_TOKEN',
        'METEOFRANCE_PIA_TOKEN',
        'METEOFRANCE_TOKEN'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   {var}: ✅ Set ({len(value)} characters)")
            print(f"      Starts with: {value[:50]}...")
            print(f"      Ends with: ...{value[-50:]}")
            
            # Compare with curl token
            if curl_token and value == curl_token:
                print(f"      🔄 MATCHES curl token exactly")
            elif curl_token and value.strip() == curl_token.strip():
                print(f"      🔄 MATCHES curl token (after trimming)")
            else:
                print(f"      ❌ DIFFERENT from curl token")
        else:
            print(f"   {var}: ❌ Not set")
    
    # Check for .env file
    print("\n📁 .env File Check:")
    if os.path.exists('.env'):
        print("   ✅ .env file exists")
        try:
            with open('.env', 'r') as f:
                content = f.read()
                print(f"   Content length: {len(content)} characters")
                
                # Look for token variables
                for var in env_vars:
                    pattern = rf'{var}\s*=\s*(.+)'
                    match = re.search(pattern, content, re.MULTILINE)
                    if match:
                        env_value = match.group(1).strip().strip('"\'')
                        print(f"   Found {var}: {len(env_value)} characters")
                        if curl_token and env_value == curl_token:
                            print(f"      🔄 MATCHES curl token exactly")
                        elif curl_token and env_value.strip() == curl_token.strip():
                            print(f"      🔄 MATCHES curl token (after trimming)")
                        else:
                            print(f"      ❌ DIFFERENT from curl token")
                    else:
                        print(f"   {var}: Not found in .env")
        except Exception as e:
            print(f"   ❌ Error reading .env: {e}")
    else:
        print("   ❌ .env file not found")
    
    print("\n=== Recommendations ===")
    if not curl_token:
        print("❌ Could not extract token from curl command")
    elif not any(os.getenv(var) for var in env_vars):
        print("❌ No environment variables set")
        print("💡 Create .env file with:")
        print(f"   METEOFRANCE_WCS_TOKEN={curl_token}")
    else:
        print("✅ Environment variables are set")
        print("💡 If tokens don't match, update .env with the working token from curl")

if __name__ == "__main__":
    main() 
import os
import sys
import requests

# Add project root to path for imports when run directly
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tests.utils.env_loader import get_env_var

url = "https://public-api.meteofrance.fr/public/arome/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS"
headers = {
    "Authorization": f"Bearer {get_env_var('METEOFRANCE_WCS_TOKEN')}"
}
params = {
    "service": "WCS",
    "version": "2.0.1",
    "request": "GetCapabilities"
}

response = requests.get(url, headers=headers, params=params)
print(f"Status Code: {response.status_code}")
print(response.text[:500])
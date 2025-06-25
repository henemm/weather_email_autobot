"""
Demo-Skript: Prüft WMS-API-Verfügbarkeit mit zwei verschiedenen Tokens (Météo-France)
"""

import os
import sys
import requests

# Add project root to path for imports when run directly
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tests.utils.env_loader import get_env_var

URL = "https://public-api.meteofrance.fr/public/arome/1.0/wms/MF-NWP-HIGHRES-AROME-001-FRANCE-WMS/GetCapabilities?service=WMS&version=1.3.0&language=eng"

# Variante 1: Direkt definierter Token
TOKEN_DIRECT = "eyJ4NXQiOiJOelU0WTJJME9XRXhZVGt6WkdJM1kySTFaakZqWVRJeE4yUTNNalEyTkRRM09HRmtZalkzTURkbE9UZ3paakUxTURRNFltSTVPR1kyTURjMVkyWTBNdyIsImtpZCI6Ik56VTRZMkkwT1dFeFlUa3paR0kzWTJJMVpqRmpZVEl4TjJRM01qUTJORFEzT0dGa1lqWTNNRGRsT1RnelpqRTFNRFE0WW1JNU9HWTJNRGMxWTJZME13X1JTMjU2IiwidHlwIjoiYXQrand0IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMjA1NzVjZi1kOGQzLTRmOWQtOWU1NC1jOTg0MWIxZTZmZmYiLCJhdXQiOiJBUFBMSUNBVElPTiIsImF1ZCI6Imx4aEQ2Q25HMjlicUNZWUNRX295T2E5UDlYQWEiLCJuYmYiOjE3NTA1ODk1MDIsImF6cCI6Imx4aEQ2Q25HMjlicUNZWUNRX295T2E5UDlYQWEiLCJzY29wZSI6ImRlZmF1bHQiLCJpc3MiOiJodHRwczpcL1wvcG9ydGFpbC1hcGkubWV0ZW9mcmFuY2UuZnJcL29hdXRoMlwvdG9rZW4iLCJleHAiOjE3NTA1OTMxMDIsImlhdCI6MTc1MDU4OTUwMiwianRpIjoiNGQ1NDViNmMtNDhmMi00OGFkLTlhNTQtY2ZkYjUwODUwOWYwIiwiY2xpZW50X2lkIjoibHhoRDZDbkcyOWJxQ1lZQ1Ffb3lPYTlQOVhBYSJ9.Q4QSmsB8KfNP5F48xHNg2ooYWZXilGOtYp21H0UFL-z7o2IUmUXqKjg4ST4mizFkgpm16p7SklwwpjE1owPgLU_yp8ZEt6hcMACmRCI4DAObNGS1_e-ElGo3UoaPkWYL7h1GQeuqWIa9syAxbq0gIDUE3p5p_rQxN6fwYQVB535bxL0wxC4e2eTdaQ0GNdnIN2CAMXkMtTP63q0o6-42Y7ymEgR8SqKrOHwlKHyPArzbii3mBLPOQhIavleewEUxD1J2YUBJIUWxyoFd7oDYydBEyqByI05hwRnSbmzrJcaGOh-OiqYodDJ7oaimTKWt7rlQD30L2jw8w-J5jelxKw"

# Variante 2: Token aus .env
TOKEN_ENV = get_env_var("METEOFRANCE_WCS_TOKEN")

def run_request(token_source, token_value):
    print(f"\n### Test mit Token aus {token_source} ###")
    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {token_value}"
    }
    response = requests.get(URL, headers=headers)
    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Preview:", response.text[:500])

# Ausführen beider Tests
run_request("direkt im Skript", TOKEN_DIRECT)
run_request(".env (METEOFRANCE_WCS_TOKEN)", TOKEN_ENV)
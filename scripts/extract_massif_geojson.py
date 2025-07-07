from playwright.sync_api import sync_playwright
import json
import os

def main():
    os.makedirs('data', exist_ok=True)
    geojsons = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        def handle_response(response):
            url = response.url
            if url.endswith('.geojson') or 'geojson' in url:
                try:
                    data = response.json()
                    geojsons[url] = data
                    print(f"[INFO] Found GeoJSON: {url}")
                except Exception as e:
                    pass
        page.on('response', handle_response)
        page.goto('https://www.risque-prevention-incendie.fr/', wait_until='networkidle')
        page.wait_for_timeout(8000)
        browser.close()
    # Speichere alle gefundenen GeoJSONs
    for i, (url, gj) in enumerate(geojsons.items()):
        fname = f"data/massif_{i}.geojson"
        with open(fname, 'w') as f:
            json.dump(gj, f)
        print(f"[INFO] Saved {fname} from {url}")

if __name__ == "__main__":
    main() 
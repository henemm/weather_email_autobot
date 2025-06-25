# Feature: Wetterwarnung abrufen (Météo France Vigilance API)

## Ziel
Ermittle aktive Wetterwarnungen für eine bestimmte Koordinate über die offizielle Météo France Vigilance API. Extrahiere die wichtigsten Informationen in eine strukturierte, wiederverwendbare Datenklasse.

## Hintergrund
Der Zugriff erfolgt über ein OAuth2-Token (JWT), das in der Umgebungsvariable `METEOFRANCE_VIGILANCE_TOKEN` bereitsteht. Die API liefert ein JSON mit u. a. folgenden Schlüsselfeldern:

- `phenomenon_max_color_id`: numerischer Warnlevel (1–4)
- `phenomenon_max_name`: z. B. "Wind", "Orage", "Pluie-inondation"
- `validity_start_date`, `validity_end_date`: ISO8601-Zeiten
- `timelaps`: enthält die eigentlichen Warnereignisse (nested)

## Anforderungen

### Funktion: `fetch_warnings(lat: float, lon: float) -> List[WeatherAlert]`
- Zugriff auf API-Endpunkt mit OAuth2 Bearer-Token
- Koordinaten via URL-Parameter (`lat`, `lon`)
- Response-Parsing der `timelaps[0]["max_colors"]` Liste
- Filtere auf Warnstufe ≥ 2 (gelb, orange, rot)
- Extrahiere pro Event:
  - Typ (`phenomenon_max_name`)
  - Warnstufe (`phenomenon_max_color_id`)
  - Beginn/Ende
- Rückgabe als Liste von `WeatherAlert`-Objekten

### Datenmodell: `WeatherAlert`
```python
@dataclass
class WeatherAlert:
    type: str  # z. B. "Wind", "Orage"
    level: int  # 1=grün … 4=rot
    start: datetime
    end: datetime
# requests/morning-evening-refactor.md

## Ziel

Ein vollständiger Neuanfang (Branch: refactor/morning-evening-v2) auf Basis des bisherigen Wissens, mit:
- Getrenntem Result-Output und Debug-Output
- Persistenter Speicherung aller aggregierten Werte zur Nachverfolgbarkeit
- Übernahme aller Format- und Verarbeitungsregeln wie spezifiziert

## Kontext

Result-Output: 
Kompakter End-Output der je nach Konfiguration per E-Mail oder SMS verschickt wird (Abend- oder Morgenbericht). Wird bei E-Mail und SMS identisch dargestellt.

Debug-Output: 
Detaillierter Export zur Nachvollziehbarkeit der Berechnungen. Wird:
- bei manueller Ausführung in der Konsole ausgegeben,
- bei E-Mail direkt nach dem Result-Output angehängt (nicht als Anhang), getrennt durch:
  
  # DEBUG DATENEXPORT

Persistenz: 
Alle berechneten Zwischenwerte werden dauerhaft gespeichert zur späteren Wiederverwendung (z. B. für Abgleich zukünftiger Berichte).

## KRITISCHE REGEL: EINHEITLICHE METHODENVERWENDUNG

**Morning und Evening Reports verwenden EXAKT die gleichen Methoden!**

- **Morning Report:** Verwendet `process_night_data()`, `process_day_data()`, etc.
- **Evening Report:** Verwendet **EXAKT DIESELBEN** `process_night_data()`, `process_day_data()`, etc.
- **Keine unterschiedliche Logik** je nach Report-Typ!
- **Nur die Input-Parameter** (Datum, Stage) unterscheiden sich

## Berichtsformen

### Morning
- Betrachtet die GEO-Punkte der heutigen Etappe für heute
- Betrachtet die GEO-Punkte der morgigen Etappe für morgen
- Debug-Output enthält: Datum heute, Etappenname heute, Anzahl GEO-Punkte; analog für morgen
- **Verwendet:** `process_night_data()`, `process_day_data()`, etc.

### Evening
- Betrachtet die GEO-Punkte der heutigen Etappe für heute
- Betrachtet die GEO-Punkte der morgigen Etappe für morgen
- Betrachtet die GEO-Punkte der übermorgen Etappe für übermorgen
- Debug-Output enthält: Datum + Etappenname + Anzahl GEO-Punkte für heute, morgen, übermorgen
- **Verwendet:** **EXAKT DIESELBEN** `process_night_data()`, `process_day_data()`, etc.

## Werte

Alle Berichte enthalten folgende Werte:

- Night (Daily Forecast) - ✅ FUNKTIONIERT
- Day (Daily Forecast) - ✅ FUNKTIONIERT
- Rain(mm) (Hourly Forecast)
- Rain(%) PROBABILITY_FORECAST | rain_3h
- Wind (Hourly Forecast)
- Gust (Hourly Forecast)
- Thunderstorm (Hourly Forecast)
- Thunderstorm (+1) (Hourly Forecast)

## FUNKTIONIERENDE IMPLEMENTIERUNGEN

### Night - FUNKTIONIERT ✅
- **API:** meteo_france / DAILY_FORECAST
- **Datenfeld:** `temp_min`
- **Struktur:** `{'T1G3': 10.7}` (letzter Punkt der Etappe)
- **Extraktion:** `daily_forecast` → `temp_min`
- **Getestet:** ✅ Funktioniert korrekt
- **Werte:** Threshold=11, Max=11
- **Debug-Output:** ✅ Vollständig mit `####### NIGHT (N) #######`

### Day - FUNKTIONIERT ✅
- **API:** meteo_france / DAILY_FORECAST
- **Datenfeld:** `temp_max`
- **Struktur:** `{'T1G1': 22.4}, {'T1G2': 29.7}, {'T1G3': 24.1}` (alle Punkte)
- **Extraktion:** `daily_forecast` → `temp_max`
- **Getestet:** ✅ Funktioniert korrekt
- **Werte:** Threshold=30, Max=30
- **Debug-Output:** ✅ Vollständig mit `####### DAY (D) #######`

### Rain(mm) - FUNKTIONIERT ✅
- **API:** meteo_france / FORECAST
- **Datenfeld:** `rain.1h`
- **Struktur:** `{"rain": {"1h": 0.5}}`
- **Extraktion:** `hour_data.get('rain', {}).get('1h', 0)`
- **Getestet:** ✅ Funktioniert korrekt
- **Debug-Output:** ✅ Vollständig mit `####### RAIN (R) #######`

### Rain(%) - FUNKTIONIERT ✅
- **API:** meteo_france / PROBABILITY_FORECAST
- **Datenfeld:** `rain_3h`
- **Struktur:** `{"rain_3h": 30}`
- **Extraktion:** `hour_data.get('rain_3h', 0)`
- **Getestet:** ✅ Funktioniert korrekt
- **Debug-Output:** ✅ Vollständig mit `####### PRAIN (PR) #######`

### Wind - FUNKTIONIERT ✅
- **API:** meteo_france / FORECAST
- **Datenfeld:** `wind.speed`
- **Struktur:** `{"wind": {"speed": 5}}`
- **Extraktion:** `hour_data.get('wind', {}).get('speed', 0)`
- **Getestet:** ✅ Funktioniert korrekt
- **Debug-Output:** ✅ Vollständig mit `####### WIND (W) #######`

### Gust - FUNKTIONIERT ✅
- **API:** meteo_france / FORECAST
- **Datenfeld:** `wind.gust`
- **Struktur:** `{"wind": {"gust": 17}}`
- **Extraktion:** `hour_data.get('wind', {}).get('gust', 0)`
- **Getestet:** ✅ Funktioniert korrekt
- **Debug-Output:** ✅ Vollständig mit `####### GUST (G) #######`

### Thunderstorm - FUNKTIONIERT ✅
- **API:** meteo_france / FORECAST
- **Datenfeld:** `weather.desc`
- **Struktur:** `{"weather": {"desc": "Averses orageuses"}}`
- **Mapping:** `'Risque d\'orages': 'low', 'Averses orageuses': 'med', 'Orages': 'high'`
- **Hinweis:** API liefert "Risque d'orages", Webseite zeigt "Orages" - beide werden erkannt
- **Threshold:** `thunderstorm_warning_level` (config.yaml)
- **Getestet:** ✅ Funktioniert korrekt
- **Debug-Output:** ✅ Vollständig mit `####### THUNDERSTORM (TH) #######`

### Debug-Output System - FUNKTIONIERT ✅
- **Format:** `####### SECTION (CODE) #######`
- **Alle Sektionen:** NIGHT, DAY, RAIN, PRAIN, WIND, GUST, THUNDERSTORM, THUNDERSTORM+1, RISKS
- **GEO-Punkte:** Alle T1G1, T1G2, T1G3 werden korrekt angezeigt
- **Threshold/Maximum-Tabellen:** Funktionieren korrekt
- **Fehlerbehandlung:** None-Vergleiche korrekt behandelt
- **Getestet:** ✅ Vollständig funktionsfähig

## Dateien

- config.yaml: startdate, thresholds
- etappen.yaml: Etappenliste mit GEO-Koordinaten (mind. 3 pro Etappe)

## Vorgaben

- Zeiten nur als Stunden ohne führende Null (z. B. 8 für 08:00 Uhr)
- Temperaturen ohne Dezimale, ganzzahlig gerundet (z. B. 9 für 9.1°C)

## Berichtselemente

### Night
Quelle: meteo_france / DAILY_FORECAST | temp_min  
Letzter Punkt der heutigen Etappe von heute

Debug-Output:
####### NIGHT (N) #######
T1G1 | 18.6
=========
MIN | 19

Result-Output:  
N8

### Day
Quelle: meteo_france / DAILY_FORECAST | temp_max  
Alle GEO-Punkte der heutigen (Morning) oder morgigen (Evening) Etappe

Debug-Output:
####### DAY (D) #######
GEO | temp_max  
G1 | 18.9  
G2 | 24.1  
G3 | 18.1  
G4 | 22.9  
=========  
MAX | 24.1

Result-Output:  
D24

### Rain (mm)
Quelle: meteo_france / FORECAST | rain  
Alle GEO-Punkte der betrachteten Etappe

Beispiel (Threshold ≥ 0.20 mm):

####### RAIN (R) #######
G1  
Time | Rain (mm)  
04:00 | 0.00  
07:00 | 0.80  
16:00 | 1.20  
=========  
07:00 | 0.80 (Threshold)  
16:00 | 1.20 (Max)

G2  
Time | Rain (mm)  
06:00 | 0.20  
07:00 | 0.80  
16:00 | 1.40  
=========  
06:00 | 0.20 (Threshold)  
16:00 | 1.40 (Max)

G3  
Time | Rain (mm)  
07:00 | 0.80  
16:00 | 1.10  
=========  
07:00 | 0.80 (Threshold)  
16:00 | 1.10 (Max)

Threshold  
GEO | Time | mm  
G1 | 7 | 0.80  
G2 | 6 | 0.20  
G3 | 7 | 0.80  
=========  
Threshold | 6 | 0.20

Maximum  
GEO | Time | Max  
G1 | 16 | 1.20  
G2 | 16 | 1.40  
G3 | 16 | 1.10  
=========  
MAX | 16 | 1.40

Result-Output:  
R0.2@6(1.40@16)

### PRain (%)
Quelle: meteo_france / PROBABILITY_FORECAST | rain_3h  
Alle GEO-Punkte der betrachteten Etappe

Beispiel (Threshold ≥ 20%):

####### PRAIN (PR) #######
G1  
Time | Rain (%)  
14:00 | 20  
17:00 | 80  
=========  
14:00 | 20 (Threshold)  
17:00 | 80 (Max)

G2  
Time | Rain (%)  
14:00 | 30  
17:00 | 100  
=========  
14:00 | 30 (Threshold)  
17:00 | 100 (Max)

G3  
Time | Rain (%)  
11:00 | 20  
17:00 | 80  
=========  
11:00 | 20 (Threshold)  
17:00 | 80 (Max)

Threshold  
GEO | Time | %  
G1 | 14 | 20  
G2 | 14 | 30  
G3 | 11 | 20  
=========  
Threshold | 11 | 20

Maximum  
GEO | Time | Max  
G1 | 17 | 80  
G2 | 17 | 100  
G3 | 17 | 80  
=========  
MAX | 17 | 100

Result-Output:  
PR20%@11(100%@17)

### Wind
Quelle: meteo_france / FORECAST | wind_speed  
Analog zu „Rain“ (Threshold in config.yaml: wind_speed)

Debug-Output
####### WIND (W) #######

[…]

Result-Output:
W10@11(15@17)

### Gust
Quelle: meteo_france / FORECAST | gusts  
Analog zu „Rain“ (Threshold in config.yaml: wind_gust_threshold)

Debug-Output
####### GUST (G) #######
[…]

Result-Output:
G20@11(30@17)

### Thunderstorm (Storm)
Quelle: meteo_france / FORECAST | condition  
Mögliche Werte:
- Risque d’orages → low
- Averses orageuses → med
- Orages → high
- sonst → none

Beispiel (Threshold ≥ med):
Debug-Output:

####### THUNDERSTROM (TH) #######
G1  
Time | Storm  
17:00 | med  
=========  
17:00 | med (Threshold)  
17:00 | med (Max)

G2  
16:00 | med  
=========  
16:00 | med (Threshold)  
16:00 | med (Max)

G3  
17:00 | med  
18:00 | high  
=========  
17:00 | med (Threshold)  
18:00 | high (Max)

Threshold  
GEO | Time | level  
G1 | 17 | med  
G2 | 16 | med  
G3 | 17 | med  
=========  
Threshold | 16 | med

Maximum  
GEO | Time | Max  
G1 | 17 | med  
G2 | 16 | med  
G3 | 18 | high  
=========  
MAX | 18 | high

Result-Output:  
TH:M@16(H@18)

### Thunderstorm (+1)
Wie Thunderstorm, jedoch +1 Etappe (+1 Tag)

Debug-Output:

####### THUNDERSTORM +1 (TH+1) #######

Result-Output:  
TH+1:M@14(H@17)

### Risks (Warnungen)
Quelle: get_warning_full()

Warnlevel:  
1 = L (Gelb)  
2 = M (Orange)  
3 = H (Rot)  
4 = R (Violett)

Events:
- Pluie-inondation → HRain
- Orages → Storm

Debug-Output

####### RISKS (HR/TH) #######

T1G1
Time | HRain | Storm
04:00 | none | none
05:00 | none | none
06:00 | none | none
07:00 | none | none
…
16:00 | M | none
17:00 | M | M
18:00 | none | none
=========HRain | 16:00 | M
Storm | 17:00 | M

T1G2
Time | HRain | Storm
04:00 | none | none
05:00 | none | none
06:00 | none | none
07:00 | none | none
…
16:00 | none | none
17:00 | H | H
18:00 | none | none
=========HRain | 17:00 | H
Storm | 17:00 | H

T1G3
Time | HRain | Storm
04:00 | none | none
05:00 | none | none
06:00 | none | none
07:00 | none | none
…
16:00 | M | none
17:00 | M | M
18:00 | none | none
=========HRain | 16:00 | M
Storm | 17:00 | M

Maximum HRain:
GEO | Time | Max
T1G1 | 16:00 | M
T1G2 | 17:00 | H
T1G3 | 16:00 | M
=========
MAX | 17:00 | M

Maximum Storm:
GEO | Time | Max
T1G1 | 17:00 | M
T1G2 | 17:00 | H
T1G3 | 17:00 | M
=========
MAX | 17:00 | H

Result-Output:
Beispiel
HR:M@17TH:H@17

### Risk (Zonale Sperrungen)
Quelle: GR20 Risk Block API

Result-Output:
Z:H208,217M:16,24

## Finaler Result-Output

Paliri: N8 D24 R0.2@6(1.40@16) PR20%@11(100%@17) W10@11(15@17) G20@11(30@17) TH:M@16(H@18) S+1:M@14(H@17) HR:M@17TH:H@17 Z:H208,217M:16,24

## Formatregeln

- Max. 160 Zeichen
- Zeit ohne führende Null
- Temperatur gerundet
- Wenn Threshold == Max: nur Threshold anzeigen
- Wenn kein Wert ≥ Threshold: Ausgabe `-`

## Speicherstruktur

Pfad:  
`.data/weather_reports/YYYY-MM-DD/{etappenname}.json`

Inhalt:  
- Schwellenzeitpunkt (Wert + Uhrzeit)  
- Maximalwert (Wert + Uhrzeit)  
- Feld, Quelle, GEO-Zuordnung

## Testschritte

1. Aufruf: `python run.py --modus morgen` bzw. `--modus abend`
2. Ergebnisoutput vollständig und korrekt
3. Debugausgabe korrekt mit Marker `# DEBUG DATENEXPORT`
4. Datenstruktur unter `.data/` vorhanden und vollständig

## Akzeptanzkriterien

- Neuer Branch `refactor/morning-evening-v2`
- Alle Outputs gemäß Spezifikation erzeugt
- Persistenz korrekt
- Schwellenlogik korrekt umgesetzt
- Kein Output > 160 Zeichen
Feature: Integrationstest mit fixer Geo-Position

Ziel

Dieser Test führt die komplette Wetteranalyse durch – basierend auf einer fest definierten Koordinate. Er überprüft, ob die Wetterdaten abgerufen, korrekt interpretiert, bewertet und ggf. als Warntext ausgegeben werden.

⸻

Anforderungen
	1.	Nutze folgende Test-Position:
	•	Breitengrad: 47.3769
	•	Längengrad: 8.5417
	•	Layer: “TEMPERATURE__GROUND_OR_WATER_SURFACE”
	2.	Konfiguration:
	•	Lies config.yaml ein
	•	Stelle sicher, dass dort risk_model und warn_thresholds definiert sind
	3.	Ablauf:
	•	WCS-Abruf über fetch_arome_wcs_data(...)
	•	Analyse via analyze_weather_data(...)
	•	Risiko-Berechnung via compute_risk(...)
	•	Text-Erzeugung über generate_warntext(...)
	4.	Ausgabe:
	•	Gib Risiko und Warntext auf der Konsole aus (print(...))
	•	Falls Warntext generiert → schreibe nach output/inreach_warnung.txt

⸻

Ziel
	•	Verifiziert, ob reale API-Daten zu nachvollziehbaren Ergebnissen führen
	•	Liefert Beispiel-Risikowerte und Texte für konkrete Orte
	•	Kann jederzeit mit neuen Koordinaten erweitert werden
    
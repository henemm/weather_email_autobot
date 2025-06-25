ANALYSE DER KONFIGURATION UND API-FÄHIGKEITEN
	1.	.env Datei (Konfiguration)

Enthält:
	•	GMAIL_APP_PW
	•	METEOFRANCE_AROME_TOKEN
	•	METEOFRANCE_VIGILANCE_TOKEN

Einschätzung:
Diese Tokens sind tokenbasierte OAuth2-Zugangsdaten. Das bedeutet: Sie laufen nach einiger Zeit ab und müssen dann per Client-ID und Client-Secret neu generiert werden. Diese Art von Token gehört nicht dauerhaft in eine .env-Datei.

Empfehlung:
Statt statische Tokens zu speichern, sollten in der .env Datei stehen:
	•	METEOFRANCE_CLIENT_ID = 
	•	METEOFRANCE_CLIENT_SECRET = 

Ein dediziertes Modul (z. B. meteo_token_provider) übernimmt den Abruf und die Erneuerung der Tokens bei Bedarf automatisch.

⸻

	2.	WMS / WCS GetCapabilities Dateien

Die bereitgestellten WMS- und WCS-Dateien enthalten Metadaten über geodatenbasierte Wetterdienste. Es handelt sich um klassische OGC-Dienste (Web Map Service, Web Coverage Service), die Layer mit verschiedenen Messwerten ausgeben können, z. B.:
	•	Sichtweite unter Niederschlag
	•	Geometrische Höhe
	•	Temperatur
	•	Niederschlagsmenge

Wichtige Erkenntnisse:
	•	Diese Dienste liefern keine konkreten JSON-Werte, sondern Karten oder Grid-basierte Daten (z. B. Bildformate oder binäre Raster).
	•	Die Layer bieten KEINE spezifischen Gewitter-Indikatoren (wie CAPE oder SHEAR).
	•	Es gibt keine offensichtliche Option, mit WMS/WCS automatisiert Strings oder Messwerte wie “Wahrscheinlichkeit für Gewitter” zu erhalten.

⸻

	3.	Gewitter-Relevanz der Parameter

Folgende Parameter aus WMS/WCS wären eventuell hilfreich für eine grobe Wetterlage:
	•	Temperatur
	•	Niederschlag
	•	Sichtweite
	•	Windgeschwindigkeit

Nicht enthalten sind:
	•	CAPE (Convective Available Potential Energy)
	•	SHEAR (Winddifferenz in vertikaler Richtung)
	•	Blitzeinschlag-Wahrscheinlichkeiten
	•	Konvektion oder Gewitterindex direkt

Fazit:
WMS/WCS nicht geeignet zur Gewitterdetektion oder -prognose.

⸻

	4.	Vigilance Bulletin

Separater Endpunkt mit strukturierten Warnhinweisen je Departement (z. B. Orange/Rot/Gelb Meldungen zu Gewitter, Sturm etc.). Geeignet zur Kombination mit numerischen Modellen wie AROME.

Beispiel:
	•	Automatischer Abgleich: Wenn CAPE×SHEAR hoch UND Vigilance sagt „Orange“, dann Gewittergefahr.
	•	Zusatznutzen: Menschlich interpretierte Risikoeinschätzung aus offiziellen Quellen.

⸻

	5.	Nächste Schritte (empfohlen)
	6.	OAuth2-Integration sauber bauen:

	•	Zugriff per CLIENT_ID + CLIENT_SECRET
	•	Token automatisch abrufen und puffern
	•	Bereitstellung des Tokens für nachgelagerte Module

	2.	JSON-basierte Forecast API inspizieren:

	•	Welche Parameter kommen zurück?
	•	Sind CAPE / SHEAR oder andere wichtige Felder enthalten?

	3.	Gewitterlogik:

	•	Regeln definieren, z. B. CAPE > 500 + SHEAR > 20
	•	Oder Kombination mit Vigilance-Level

	4.	API-Module:

	•	fetch_forecast_data
	•	parse_forecast_result
	•	interpret_forecast_thunderstorm_risk
Refactoring: Meteo-France Token-Provider vereinheitlichen

Ziel

Das Projekt nutzt aktuell pro API-Aufruf eine neue Instanz des MeteoTokenProvider, was zu mehrfachen Tokenanforderungen führt – trotz implementierter Cache-Logik. Zudem ist unklar, welche APIs welchen Token benötigen.

Ziel dieses Refactorings ist es:
	1.	eine Singleton- oder modulare Instanz des Token-Providers bereitzustellen
	2.	die Wiederverwendbarkeit über alle Meteo-France APIs hinweg sicherzustellen
	3.	volle Transparenz und Logging über alle Token-Zustände zu ermöglichen

⸻

Hintergrund
	•	Alle Meteo-France APIs einer Anwendung nutzen denselben OAuth2-Token, sofern dieser nach Abo aller APIs generiert wurde
	•	Es gibt aktuell drei relevante APIs:
	•	AROME WCS (z. B. Temperatur, CAPE, CIN)
	•	Vigilance Bulletins
	•	AROME Forecast JSON API (Swagger: Immediate Forecast)
	•	Derzeit erzeugt jeder Aufruf von fetch_arome_wcs_data oder fetch_vigilance eine neue Instanz – dadurch mehrfacher, unnötiger Tokenabruf

⸻

Anforderungen

Token-Verwaltung
	•	Der MeteoTokenProvider wird als Singleton oder modul-globaler Cache implementiert
	•	Der Token wird einmalig abgerufen, gespeichert und bei weiteren Aufrufen wiederverwendet, solange er gültig ist
	•	Optional: Automatische Erneuerung, falls Token abgelaufen (HTTP 401 mit typischem Fehlertext)

Logging & Transparenz
	•	Jeder Tokenabruf wird geloggt: Zeitpunkt, Gültigkeitsdauer, verwendete Methode
	•	Bei Wiederverwendung: „Using cached token“ o. ä. in Debug-Log
	•	Optional: Logging der Authorization-Header (verkürzt / maskiert) zum Debugging

Fehlerverhalten
	•	Token fehlt: RuntimeError mit verständlicher Fehlermeldung
	•	Fehlerhafte Authentifizierung (HTTP 401): Erneuter Versuch mit neuem Token
	•	Alle anderen HTTP-Fehler: Unverändert weitergeben

Kompatibilität
	•	Die Änderungen dürfen keine bestehende API-Funktionalität brechen
	•	Tests für fetch_arome_wcs_data, fetch_vigilance, etc. müssen weiterhin grün laufen
	•	Neue Tests müssen ergänzt werden:
	•	Wiederverwendung des Tokens
	•	Fallback bei 401
	•	Token-Abruf-Logging

⸻

Ablageorte
	•	Token-Provider: src/auth/meteo_token_provider.py
	•	Globale Instanz: ggf. src/auth/token_instance.py oder direkt als Modulvariable
	•	Tests: tests/test_meteo_token_provider.py

⸻

Hinweise
	•	Verwende das offizielle Beispiel aus der Météo-France Swagger-Dokumentation als Referenz für Ablauf
	•	Bei Unsicherheiten: https://portail-api.meteofrance.fr → Benutzer-Dashboard → API-Abos prüfen
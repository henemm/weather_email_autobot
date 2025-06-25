Ziel:
Entfernung aller Emoji aus dem System, da sie bei Versand über SOTAmāt an Garmin-Geräte nicht korrekt dargestellt werden.

Maßnahmen:
	1.	Funktion get_risk_emoji entfernen:
	•	Datei: src/notification/email_client.py
	•	Die Funktion, die Emojis basierend auf Risikostufen zurückgibt, wird vollständig entfernt.
	2.	Emoji-Nutzung in Berichten eliminieren:
	•	Alle Stellen im Code, wo Emojis in E-Mails eingefügt werden, müssen bereinigt oder durch neutrale Textsymbole ersetzt werden (z. B. „WARNUNG“ statt ⚠️).
	3.	Tests anpassen:
	•	Datei: tests/test_email_client.py
	•	Testfälle, die Emoji prüfen oder enthalten, müssen angepasst werden.
	•	Es soll ein expliziter Test sichergestellt werden, dass der generierte Bericht emoji-frei ist.

Akzeptanzkriterien:
	•	Kein Emoji im generierten Report.
	•	Alle relevanten Tests bestehen.
	•	Versand funktioniert mit Garmin über SOTAmāt ohne Zeichenfehler.
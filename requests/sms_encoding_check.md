# SMS Encoding Validierung für GSM-7

## Ziel
Sicherstellen, dass alle SMS-Texte im GSM-7-Zeichensatz bleiben, um eine UCS-2-Kodierung und Mehrteiligkeit zu vermeiden. Dadurch werden Probleme mit der Zustellung über seven.io reduziert und unnötige Mehrkosten vermieden.

## Hintergrund
Einige empfangene SMS (z. B. ID: 77272893231) verwenden UCS-2-Kodierung und enthalten mehr als ein Nachrichtenteil. Diese Nachrichten verursachen unerwartetes Verhalten im Empfangs- und Journal-System von seven.io.

## Anforderungen

### 1. Zeichenprüfung vor SMS-Versand
- Vor dem Versand einer SMS muss der vollständige Text gegen die Zeichenliste des GSM-7-Zeichensatzes geprüft werden.
- Wenn ein Zeichen außerhalb dieses Zeichensatzes liegt, soll die SMS **nicht** gesendet werden.
- Stattdessen:
  - Ein Fehler wird geloggt (z. B. `sms_encoding_violation.log`)
  - Eine kurze Zusammenfassung der problematischen Zeichen wird mitprotokolliert

### 2. Abbruchbedingung
- Falls eine Verletzung festgestellt wird, muss der SMS-Versand **vollständig abgebrochen** werden.

### 3. Zeichen-Whitelist (GSM-7)
Zulässige Zeichen sind unter anderem:
@£$¥èéùìòÇ\nØø\rÅå_ÆæßÉ !”#¤%&’()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà

(Siehe auch: [offizielle GSM 03.38-Tabelle](https://en.wikipedia.org/wiki/GSM_03.38))

### 5. Logging
- Log-Datei: `output/logs/sms_encoding_violation.log`
- Eintrag bei Verstoß:
[2025-07-08 13:52] Abbruch SMS-Versand: Ungültige Zeichen im Text gefunden.
Zeichen: „ö“, Position: 63, Kontext: „…Böen14…“
Absender: SMS-Modul Wetterbericht
## Umsetzung
- Prüfung soll in der zentralen SMS-Sende-Funktion erfolgen (`sms/send_sms()` oder vergleichbar)
- Kein zusätzlicher Parameter erforderlich – gilt pauschal für alle SMS

## Testszenarien
- ✅ Gültige GSM-7 Nachricht (siehe Beispiel): wird versendet
- ❌ Nachricht mit „ß“, „ö“, typografischen Anführungszeichen oder Emojis: Versand wird abgebrochen, geloggt

## Umsetzung
- Prüfung soll in der zentralen SMS-Sende-Funktion erfolgen (`sms/send_sms()` oder vergleichbar)
- Kein zusätzlicher Parameter erforderlich – gilt pauschal für alle SMS

## Testszenarien
- ✅ Gültige GSM-7 Nachricht (siehe Beispiel): wird versendet
- ❌ Nachricht mit „ß“, „ö“, typografischen Anführungszeichen oder Emojis: Versand wird abgebrochen, geloggt

bitte email_format.mdc aktualisieren
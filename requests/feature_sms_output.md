# requests/feature_sms_output.md

## Titel

Versand von Wetterberichten per SMS über seven.io

## Ziel

Zusätzlich zur E-Mail sollen alle Wetterberichte (Morgen-, Abend- und dynamische Warnungen) auch per SMS über den Dienst seven.io an eine konfigurierbare Telefonnummer versendet werden.

## Anforderungen

### 1. Versandmethode
- Der SMS-Versand erfolgt ausschließlich über die HTTP REST API von seven.io.
- Es wird keine SMTP-Weiterleitung, kein lokaler SMS-Dienst oder andere Gateways verwendet.

### 2. Konfiguration
- Die Einstellungen für den SMS-Versand befinden sich in `config.yaml`:
  sms:
    enabled: true
    provider: seven
    api_key: "<SEVEN_API_KEY>"
    to: "+4916092170813"
    sender: "GR20-Info"

### 3. Inhalt
- Die gesendete SMS verwendet exakt den gleichen Text wie die InReach-E-Mail.
- Format: Ultrakompakt (max. 160 Zeichen), keine Emojis, keine Formatierung.

### 4. Sendezeitpunkte
- SMS werden versendet bei:
  - Abendbericht
  - Morgenbericht
  - Dynamische Warnung (sofern generiert)

### 5. Implementation
- HTTP POST an:
  https://gateway.seven.io/api/sms
- Header:
  Authorization: Bearer <api_key>
- Body (Form-Encoded):
  to=<Zielnummer>
  from=<Absendername>
  text=<Berichtstext>

### 6. Fehlerverhalten
- Fehlerhafte Anfragen (z. B. falscher API-Key) werden im Log vermerkt.
- Die Verarbeitung wird nicht abgebrochen – E-Mail-Versand bleibt unabhängig.

## Validierung

- Eine SMS wird mit realem Berichtstext über seven.io erfolgreich versendet.
- Empfang auf Zielgerät geprüft.
- Fehlerhafte Konfiguration wird erkannt und geloggt.
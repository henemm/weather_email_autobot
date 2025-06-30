# Modularisierung des SMS-Versands

## Ziel

Der SMS-Versand soll so modularisiert werden, dass weitere Provider (z. B. Twilio) einfach ergänzt und konfiguriert werden können. Der aktuelle seven.io-Versand dient als erste Implementierung eines SMS-Providers.

## Anforderungen

### Architektur

- Erstelle eine Schnittstelle bzw. abstrakte Basisklasse `SmsProvider` mit der Methode:
  - `send_sms(to: str, message: str) -> bool`

- Implementiere den bestehenden seven.io-Versand als konkreten Provider:
  - `SevenProvider(SmsProvider)`

- Ermögliche die Konfiguration des gewünschten Providers über `config.yaml`:
  ```yaml
  sms:
    provider: seven
    seven:
      api_key: "..."
      from: "491601234567"
    twilio:
      account_sid: "..."
      auth_token: "..."
      from: "+14151234567"

# X^∞ CapGate Mesh System – Technische Dokumentation

## 1. Systemkomponenten

### Gate-Knoten
Jeder CapGate-Knoten ist ein autarkes Gerät mit:
- BLE/WiFi-Scanfunktion (z. B. Raspberry Pi, ESP32, Android Edge-App)
- CapValidator-Modul
- AuditLogger
- GateSync-Modul für bidirektionale Mesh-Verknüpfung

### CapDevice
Sendet CapToken via BLE oder NFC
- enthält Cap-Werte, Rolle, Gültigkeit, Signatur

---

## 2. Domänenspezifische Wallets

Jeder Nutzer hat für jede Wirkungskontext-Domäne eine eigene Wallet (z. B. Sozial, Infrastruktur, Bildung).
Gate-Knoten verwenden diese Struktur zur:
- Signierung aller MAC-Daten und Präsenzmeldungen
- Isolierung auditierbarer Zonen

---

## 3. GateSync-Mechanismus

### Senden:
- Scanlog (`seen_devices_log`) wird als JSON exportiert
- automatisch signiert mit Domänenwallet
- gespeichert in `last_sync_out.json`

### Empfangen:
- andere Gates senden signiertes Log
- Daten werden geprüft und gespeichert in `synced_seen_log.json`

### Format:
```json
{
  "gate_wallet": "0xABC...",
  "timestamp": 1714800000,
  "seen": [{ "mac": "...", "rssi": -55 }],
  "signature": "signed_by:0xABC..."
}
```

---

## 4. Sicherheitsmerkmale

- keine anonymen Daten im Netzwerk
- vollständige Rückverfolgbarkeit über Wallet und Domain
- auditierbare Knoten
- verteilte Mesh-Redundanz zur Manipulationsabsicherung

---

## 5. Nächste Schritte

- echte Signierung via eth-crypto
- Signaturprüfung auf Empfangsseite (CapValidator erweitern)
- BLE-Relay zwischen mobilen Gates zur Reichweitenkopplung

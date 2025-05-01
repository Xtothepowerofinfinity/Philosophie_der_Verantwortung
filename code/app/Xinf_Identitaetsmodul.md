
# X^∞ Identitätsmodul – Domänenspezifische Wallet-Architektur

## 1. Grundprinzip

Im X^∞-Modell besitzt jede Entität nicht *eine* zentrale Identität, sondern eine **Wallet pro Wirkungskontext-Domäne**.

Beispiele:
- `"0xABC..."` → Infrastruktur (CapGate, Projektleitung)
- `"0xDEF..."` → Sozial (Rückmeldung, Teilnahme)
- `"0x123..."` → Bildung (Lernprojekte, Schülerfeedback)

Diese Trennung ermöglicht:
- vollständige Auditierbarkeit *innerhalb* eines Kontextes
- vollständige Anonymität *zwischen* Kontexten

---

## 2. Vorteile

| Merkmal            | Wirkung                             |
|--------------------|--------------------------------------|
| 🧾 Kontextklarheit  | Cap, Rolle und Verantwortung eindeutig |
| 🔒 Anonymisierung   | Keine Cross-Domänen-Korrelation       |
| 🔁 Wiederverwendbarkeit | Wallets können je nach Rolle reaktiviert werden |
| 🧠 Schutz vor Missbrauch | Kein Identitätsprofiling möglich     |

---

## 3. Technische Umsetzung

### Wallet-Verwaltung
- CapDevice-App verwaltet pro Nutzer mehrere Wallets
- Zuweisung nach Kontext oder QR-Initialisierung
- privateKeys werden lokal gespeichert (verschlüsselt, sandboxed)

### Automatische Signatur
- Bei Aktionen (Feedback, GateSync, TokenAuth) wird automatisch die passende Wallet verwendet
- Signierung erfolgt im Hintergrund, z. B.:
```dart
signWithWallet("infra", payload) => uses 0xABC...
signWithWallet("social", payload) => uses 0xDEF...
```

---

## 4. Gate-Verwendung

- Jeder Gate-Knoten hat **eine Domänenwallet** (z. B. `"infra"`)
- Alle `seen_logs` und `sync_data` werden damit signiert
- Rückverfolgbarkeit + Mesh-Integrität

---

## 5. Relevanz für die Masterstruktur

Diese Architektur ersetzt zentrale IDs und ermöglicht:
- skalierbare Gesellschaftsstruktur
- projektübergreifende Resilienz
- hochsichere, kontextgetrennte Autorisierung

---

## 6. Erweiterungsidee

- **CapScopedToken** → Token nur innerhalb einer Domäne gültig
- **Domänenübergreifende Aggregation** → nur durch autorisierte Knoten mit Metacap


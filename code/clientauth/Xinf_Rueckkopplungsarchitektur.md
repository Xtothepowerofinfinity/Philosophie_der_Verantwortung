
# X^∞ Rückkopplungsarchitektur – Spezifikation v1.0

## Ziel
Jede Wirkung im System muss rückverfolgbar, cap-basiert und signiert dokumentiert werden – abgestuft nach Relevanz und Eskalationsgrad.

---

## 1. Zustandsmodelle der Rückkopplung

### 🟢 1. Normalzustand
- Regelmäßige Monitoringpunkte
- Signierte Telemetrie mit Cap-Zuordnung
- Frequenz: konfigurierbar (z. B. alle 5 Minuten)
- Inhalte:
  - CapSession (wallet, role, scope)
  - Prozess, Ressource, Wirkung
  - Messwerte (CPU, Netz, Files, Timing)
  - AuditHash der CapToken-Session

**Beispiel:**
```json
{
  "type": "monitoring",
  "wallet": "0xABC...",
  "process": "daemon/gateway",
  "cap_scope": ["proc:/monitor"],
  "metrics": {
    "cpu": 0.14,
    "net_latency": 12,
    "cap_health": 1.0
  },
  "signature": "0x..."
}
```

---

### 🟡 2. Event-Zustand
- Ausgelöst bei Grenzwertüberschreitung oder ungewöhnlicher Korrelation
- Sofortmeldung, ohne Zeitverzug
- Cap-Zuordnung verpflichtend
- wird persistent abgelegt und an CapAudit-Daemon gemeldet

**Beispiel:**
```json
{
  "type": "event",
  "wallet": "0xDEF...",
  "trigger": "CPU > 95%",
  "process": "worker/pdf_batcher",
  "cap_scope": ["proc:/batch"],
  "impact": "latency_peak",
  "signature": "0x..."
}
```

---

### 🔴 3. Incident-Zustand
- Systemisch relevante Fehlfunktion mit potenzieller Wirkungskaskade
- Detailbericht zwingend, signiert, nicht unterdrückbar
- beschreibt:
  - Auslöserprozess + PID
  - CapToken + Rolle
  - beschädigte Objekte (z. B. Datenbank, Struktur, Kernel-Flag)
  - Zeitstempel, Host, Rückverfolgbarkeit

**Beispiel:**
```json
{
  "type": "incident",
  "wallet": "0xAAA...",
  "role": "infra.dbwriter",
  "affected_asset": "capfs:/db/userdata.sqlite",
  "status": "corrupted",
  "access_process": "api/write",
  "cap_scope": ["fs:/db"],
  "signature": "0x...",
  "timestamp": 1715019911
}
```

---

## 2. Sicherheit & Eskalation

- Jede Rückkopplung wird durch CapAuditServer entgegengenommen
- Ereignisse mit Phantomursprung werden anonymisiert, aber trotzdem signiert
- Wiederholte Events ohne Handlung → triggern strukturelle Auditmeldung

---

## 3. Optional: Signierte Quittungen

- Jeder Rückkopplungseintrag erzeugt eine Quittung
- Enthält Hash, Zustandsstufe, Zeit und Prüfsumme
- Wird von CoreNode rückbestätigt oder verworfen

---

## 4. Ziel
> Wirkung ≠ Gefühl. Rückkopplung dokumentiert messbare Realität – und schützt das System, nicht das Ego.


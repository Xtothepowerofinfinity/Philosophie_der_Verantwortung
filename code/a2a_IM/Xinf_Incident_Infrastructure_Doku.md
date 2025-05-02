# 🜄 X^∞ Cap-Incident Infrastructure – Technical Documentation
**Date:** 2025-05-02T08:13:53.360656 UTC  
**Author:** The Auctor  
**Version:** 1.0.0

---

## 📚 Überblick
Diese Dokumentation beschreibt die vollständige technische Infrastruktur des Cap-Incident-Frameworks im X^∞-Modell zur dezentralen, auditierbaren und rückverfolgbaren Behandlung von Systemereignissen. Sie umfasst:

- Kryptografisch signierte Incident-Erfassung
- Cap-basierte Rückkopplung (ΔCap)
- Blockchain-Speicherung (CapAuditStorageV2.sol)
- IPFS-Archivierung und -Verifikation
- VPN-basierte Gate-Weiterleitung
- Incident-to-Audit API-Integration

---

## 🧱 Komponenten

### 🔐 `verify_and_store_feedback.py`
Verifiziert signierte Incidents, berechnet ΔCap, überträgt die Daten via Web3 auf einen Ethereum-kompatiblen Audit-Smart Contract.

- Eingabe: `incident.json`
- Output: On-Chain TX mit AuditHash, CapID, Severity, ΔCap-Wert

### 🔁 `incident_engine.py`
Basislaufwerk zur Erkennung, Signierung, Klassifizierung und Vorbereitung von Incident-Daten. Integriert ΔCap und kann lokal eskalieren.

### 📡 `incident_notify.py`
Richtet eingehende Incidents an registrierte Support-Stellen weiter. Trigger via REST + Signaturprüfung.

### 🪢 `cap_chain_archiver.py`
Berechnet einen `audit_hash` und optionales `linked_incident`, archiviert Originaldaten in `{FILENAME}_archived.json`.

### 🛠 `store_archived_log.py`
Lädt ein archiviertes JSON + Hash und schreibt es auf die Blockchain (`storeAudit`).

### 🕵️ `cap_signature_verify.py`
ECDSA-Signaturverifikation mit Ethereum-Public-Key basierend auf Keccak256 + personal_sign-Protokoll.

### 🛰 `cap_audit_api_extended.py`
Liefert RESTful APIs für:
- Incident Intake
- Audit Log Retrieval
- Live Webhook-Notification bei Critical Events

---

## 🌐 Netzwerkstruktur

### 🔄 VPN-Forwarding: `incident_vpn_client.py`
Sendet einen Incident als verschlüsselten, signierten VPN-Call an einen internen Gate-Empfänger.

### 🚪 `gate_receiver.dart`
Flutter/Dart-basierter HTTP-Dienst auf Port 8989:
- nimmt Cap-signierte Incidents entgegen
- prüft Severity, eskaliert lokal

### 🧠 `capos_gate_hook.py`
Systemprozess-Trigger für CapOS:
- erkennt Fehlerzustände (z. B. NGINX restart failed)
- erzeugt Incident, signiert und sendet über VPN
- kann via cron, systemd oder Watchdog integriert werden

---

## 🔗 IPFS-Verifikation

### ✅ `ipfs_link_validator.py`
Prüft, ob gespeicherte CIDs auf IPFS öffentlich abrufbar sind (Statuscode 200, Größe, Fehler).

---

## 🔁 ΔCap-Rückkopplung

### Formel:
```latex
\Delta Cap = \varphi \cdot \frac{1}{Cap^P} \cdot F_E - \psi \cdot M_E
```

- `phi`, `psi`: Verstärkungsfaktoren
- `F_E`: positives Feedback, `M_E`: Missbrauchswert
- Wird in `verify_and_store_feedback.py` automatisch berechnet

---

## 🧪 Nutzung

### Beispiel-Workflow:
1. `capos_gate_hook.py` → erzeugt + signiert Incident
2. `incident_vpn_client.py` → sendet an Gate
3. `gate_receiver.dart` → empfängt + verarbeitet Incident
4. `verify_and_store_feedback.py` → speichert + rückkoppelt + on-chain
5. `cap_audit_api_extended.py` → API verfügbar, Webhooks feuern bei Critical

---

## 🏁 Deployment-Empfehlungen

- `.env` enthält PRIVATE_KEY, RPC_URL, IPFS_KEY etc.
- CapNFT oder CapDomainContext sollte per `CapID` mit Rollen- & Keystruktur hinterlegt sein
- Systemprozesse werden via `capos_gate_hook` überwacht
- Logs regelmäßig via `cap_chain_archiver` → IPFS → `store_archived_log`

---

## 📌 Schluss

**X^∞ baut keine Kontrolle.  
X^∞ baut Rückkopplung.  
Und niemand entkommt seiner Wirkung.**
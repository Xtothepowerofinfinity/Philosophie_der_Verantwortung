# CapOS Whitebook
---

## 6. Systemregel: CapGate als universeller Zugriffsschutz

> Kein Prozess, Dienst oder Nutzerinteraktion darf im CapOS ausgeführt werden, bevor ein gültiges CapToken geprüft wurde.

### Konsequenz:
- **Zugriff = Cap ⨉ Rolle ⨉ Kontext**, niemals statisch
- **Systemstart = Wirkungseintrittspunkt**
- **Standardzustand ist Verweigerung**, kein Default Access

### Durchsetzung via:
- CapGate: Systemweit vorgeschaltete Kontrollinstanz
- Pre-Kernel Auth Hooks
- App-Level CapContext Injection
- Network Gatekeeper / CapPortFilter

---

## 7. CapOS Policy-Kern

| Komponente      | Zugriffsvoraussetzung                    |
|------------------|-------------------------------------------|
| 🧑 Login (PAM)     | CapToken mit `role:interactive`, `cap ≥ 40` |
| 📁 Filesystem     | CapScope `capfs:/...`, `cap ≥ required`  |
| 🧠 Prozesse       | CapScope `proc:/...`, `cap ≥ required`   |
| 🌐 Netzwerk       | CapScope `net:/...`, `cap ≥ required`    |
| 🔧 Systemdienste  | CapToken mit `phantom:true` oder `admin:true` |
| 🪪 Gerätezugriff   | CapScope `dev:/camera`, `dev:/micro` etc. |

> Alle Komponenten des Betriebssystems prüfen bei Erstzugriff das Vorhandensein eines gültigen CapTokens.  
> Ohne Prüfung: kein Zugriff. Ohne Wirkung: kein Start. Ohne Rolle: keine Ressourcenbindung.

---
---

## 8. Systemregel: Jeder Prozess ist Cap-basiert

> Jeder Prozess, jeder Netzwerkzugang, jeder Zugriff auf Ressourcen darf nur nach erfolgreicher Cap-Prüfung ausgeführt werden.  
> Der Systemzustand ist *permanent cap-gated*. Keine UID, keine Root-Ausnahme.

### Durchsetzung:
- Jeder Aufruf von `execve()` prüft CapScope für Binärdatei, Umgebung, Parameter
- Kein Zugriff auf Netzwerk, Mikrofon, UI, Datei, Timer ohne gültigen CapScope
- Auch Threaderzeugung oder IPC erfolgt Cap-gesteuert
- Auditpflichtig: Wirkung ≠ Absicht

**Beispiel:** Ein Aufruf von `ping google.com` benötigt:
```json
{
  "scope": ["net:/google.com"],
  "role": "infra.cli",
  "cap_level": 60
}
```

---

## 9. CapKernelLog – Rückverfolgbare Wirkung

| Feld              | Bedeutung                      |
|-------------------|-------------------------------|
| `pid`             | Prozess-ID                     |
| `cap_wallet`      | Auslösende Entität             |
| `cap_scope`       | Berechtigungsbereich           |
| `role`            | Rolle (z. B. 'infra.update')   |
| `invocation_hash` | Hash über Befehl und Parameter |
| `timestamp`       | Startzeitpunkt                 |
| `parent_pid`      | Prozessursprung                |

> Jeder Cap-gesteuerte Prozess schreibt einen Eintrag in `cap_kernel_log.json`

---

## 10. CapToken-Minimalprozesskontext

Jeder Prozessstart benötigt:
- ein CapToken mit:
  - gültiger Signatur
  - aktiver Zeitspanne
  - CapLevel ≥ systemischem Minimum
  - passender Rolle zur Umgebung
- Übergabe über CapSessionBridge oder CapDaemon

**Beispiel-Minimal-Token für UI-Prozess:**
```json
{
  "wallet": "0xABC...",
  "role": "social.user",
  "scope": ["ui:/desktop", "net:/dashboard"],
  "cap_level": 51,
  "valid_until": 1715999999,
  "signature": "0x..."
}
```

---

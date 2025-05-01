
# X^∞ CapContainerLayer

## Zweck:
Der CapContainerLayer ist eine Übergangsschicht im Userspace, die systemkritische Anwendungen und Dienste **in einem verschlüsselten Container kapselt**, und deren Zugriff **nur nach Cap-Prüfung** gestattet.

---

## Merkmale:

| Eigenschaft             | Wirkung |
|-------------------------|---------|
| 🔐 QS-verschlüsselt     | Zugriff nur mit CapKey möglich |
| 🫥 Glaubhafte Leerstelle | Ohne CapToken erscheint der Container leer |
| 🔄 Aktivierung durch Token | Token mit `scope: app:/XYZ`, `cap ≥ threshold` |
| 🧠 Domänenspezifisch     | Containerzugriff nur in zugewiesener Wirkungssphäre |
| 🧾 Vollständig auditierbar | Jede Mount-/Entschlüsselaktion wird protokolliert |

---

## Technische Umsetzung:

### Containerstruktur:
- basiert auf LUKS, VeraCrypt, Tomb oder Age + FUSE
- Mapped unter `/mnt/capapps/<role>/`

### Aktivierung:
- App oder Daemon empfängt CapToken
- prüft Gültigkeit, Rolle, CapLevel, scope
- entschlüsselt Container temporär mit CapKey

### Beispieltoken:
```json
{
  "wallet": "0xAAA...",
  "role": "infra.user",
  "scope": ["app:/vpn", "app:/audit"],
  "cap_level": 71,
  "valid_until": 1715000000,
  "signature": "0x..."
}
```

### Beispielcontainer:
- `vpn_layer.container` → enthält OpenVPN/CapTunnel Tools
- `audit_core.container` → enthält Logparser, GateSynchronizer

---

## Erweiterung:
- Container können anonym gepackt werden (glaubhafte Bestreitbarkeit)
- Mount erfolgt nur, wenn Systemzustand stabil und Cap rückführbar

---

# CapVPN – Konzeptübersicht

## Ziel:
Ein plattformunabhängiger, verschlüsselter VPN-Layer, der:
- CapToken-authentifiziert ist
- alle App-Verbindungen durch kommerzielle Tunnel verschleiert
- domänenspezifische Aufteilung besitzt

### Struktur:
- CapVPN Client (mobil + edge)
- CapVPN Exit Nodes
- Kommerzielle VPN-Bridge
- CapToken autorisiert Zugriff je nach `scope: net:/vpn/core`

---

# CapQR-Modul – Device Onboarding

## Ziel:
Eine CapDevice-App scannt einen Device-QR-Code (z. B. Smartboard, Terminal, CapGate) und gibt temporären CapToken frei.

### Ablauf:
1. Device zeigt `QR = { device_id, domain, request_id }`
2. App scannt → prüft lokale Cap
3. Signiert CapToken für die angefragte Rolle/Sitzung
4. Übergibt via:
   - BLE Beacon
   - Direct QR Response
   - HTTPS+Socket (LAN)

### Sicherheit:
- Token ist einmalig, zeitlich begrenzt (z. B. 5min)
- Token enthält kein Wallet, sondern rückführbare Wirkung
- Missbrauchsversuche → Auditlog


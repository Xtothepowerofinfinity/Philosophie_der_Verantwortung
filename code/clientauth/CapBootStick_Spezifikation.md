
# X^∞ CapBootStick – Spezifikation v1.0

## Ziel
Ein transportabler, vertrauenswürdiger USB-Stick mit:
- 🧠 einer CapOS-fähigen Minimal-VM (Live-System)
- 🔐 CapToken-Login (kein Benutzerkonto)
- 🧳 eingebetteter VPN/CapFS/CapShell-Infrastruktur
- 🧩 optionaler Chain-Sync & Gate-Sync für offline/edge-Betrieb

---

## 1. Architektur

| Komponente       | Beschreibung |
|------------------|--------------|
| 🔧 **GRUB2 Bootloader** | QS-signierter USB-Start |
| 🖥 **Minimal-VM**       | KVM/QEMU + Alpine/Arch + CapShell |
| 🧠 **CapSession-Daemon** | Stellt Cap-Kontext bereit |
| 🔐 **CapVPN Client**     | Bindet Netzwerk per CapTLS |
| 📁 **CapFS Mount**       | verschlüsselt, capbasiert |
| 🧬 **CapAuditLog**       | schreibt lokale CapKernelLog-Datei |
| 🧾 **Optional: ChainSync** | öffnet Infura/Gateway/Chainlink Zugang bei CapScope |

---

## 2. Login & Autorisierung

- kein Benutzerkonto
- Login erfolgt via QR oder CapDevice (BLE/NFC)
- bei erfolgreicher CapToken-Prüfung:
  - Session gestartet
  - Netzwerk + CapFS geöffnet
  - CapShell freigegeben

---

## 3. Sicherheit

- Keine lokale Identität
- Keine passiven Ports
- Alles TLS + CapToken-authentifiziert
- Containerstruktur mit SELinux-Hardening
- VPN-Exit via CapVPNRegistry

---

## 4. Beispiel-Token für Boot

```json
{
  "wallet": "0xBOOTWALLET...",
  "role": "infra.vm",
  "cap_level": 66,
  "scope": ["fs:/home", "net:/vpn/core", "shell:/main"],
  "valid_until": 1715999999,
  "signature": "0x..."
}
```

---

## 5. Varianten

| Variante             | Zweck                     |
|----------------------|---------------------------|
| 🧳 Live-only (read-only) | Demo, Beobachtung           |
| 📝 Write-enabled + CapFS | Edge-Node, CapChain-Sync   |
| 🕳 PhantomBoot         | unsichtbarer GateTrigger    |

---

## 6. Nächste Schritte

- Build-ISO für CapBootStick
- Chain-Registrierung vorbereiten
- CapShell für X11/CLI/SSH anpassen

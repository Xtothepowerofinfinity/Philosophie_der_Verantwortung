
# X^∞ CapDevice AppVPN Integration

## Ziel
Alle Netzwerkverbindungen der CapDevice-App laufen über den CapVPN-Stack.  
Die Verbindung erfolgt CapToken-gesteuert, domänenspezifisch, vollständig auditiert und durch kommerzielle Dienste getunnelt.

---

## Architektur

1. **VPN Resolver**:
   - liest Domain-VPN-Exit aus Blockchain (CapVPNRegistry)
   - z. B. `getNode("infra", hash(wallet) % count)`

2. **CapToken Authenticator**:
   - signiert Challenge mit Wallet (CapTLS handshake)
   - sendet `wallet`, `cap_token`, `signature` an ExitNode

3. **VPN Client (App-Level)**:
   - startet CapTLS-Handshake
   - verschlüsselt Traffic
   - nutzt vorhandene VPN-Protokolle (WireGuard, OpenVPN) als Transport

4. **Audit Logger**:
   - loggt: `timestamp`, `wallet`, `domain`, `exit_node`, `duration`
   - optional PhantomMasking

---

## Flutter Komponenten

### cap_vpn_controller.dart
- koordiniert Chain-Resolver, CapSession, Tunnelstarter

### cap_vpn_resolver.dart
- verwendet `CapVPNChainResolver` um Exit-IP zu holen

### cap_tls_client.dart
- startet TLS-Session mit Wallet + CapToken Auth

### cap_vpn_log.dart
- auditiert jede Verbindung, speichert lokal + optional remote

---

## UI

| Ansicht            | Elemente                          |
|--------------------|-----------------------------------|
| VPN-Statusseite     | Aktiver Domain-VPN, Zeit, ExitNode |
| Verbindung starten | Switch mit Auswahl `infra`, `social` etc. |
| Historie           | Letzte Sessions, Auditcode        |

---

## Sicherheit

- TLS 1.3 mit Walletsignatur + CapToken
- Kein Default Access ohne Token
- Exit-Node prüft on-chain Authentizität
- Fallback-Tunnel über kommerziellen Multi-Hop (optional)

---

## Beispiel-Token
```json
{
  "wallet": "0xAAA...",
  "role": "infra.vpn",
  "scope": ["net:/vpn/core"],
  "cap_level": 77,
  "valid_until": 1715111100,
  "signature": "0x..."
}
```

---

## Nächste Schritte

1. Bootstick mit CapVM + CapShell
2. CapRückkopplungskern


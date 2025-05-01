
# Chainfeed für Rückkopplungs-Eskalation

## Ziel
Wichtige Rückkopplungsereignisse (z. B. Incidents) werden durch CapAuditDaemon automatisch in eine on-chain Nachricht übersetzt – z. B. als Event oder als Storage-Eintrag im CapChain-Kernvertrag.

---

## Mechanismus

1. CapAuditDaemon erkennt `type: incident`
2. Signatur & CapToken validiert
3. Chainfeed-Modul formatiert Daten als:
   - z. B. Hash(message), wallet, cap_scope, timestamp
4. sendet an:
   - Chainlink Adapter
   - Ethereum L2 (z. B. Polygon, Arbitrum)
   - oder speichert im StorageContract

---

## Beispiel: Incident-Ereignis auf Chain
```solidity
event IncidentReported(
    address indexed wallet,
    string scope,
    string hash,
    uint256 timestamp
);
```

## Sicherheit
- Walletsignatur prüfbar auf-chain
- Inhalt bleibt optional off-chain (Datenschutz)
- Rückwirkung ist öffentlich und auditierbar

## Erweiterung
- Notfalltrigger (z. B. `shutdown_core`)
- PhantomReports mit anonymem Hash


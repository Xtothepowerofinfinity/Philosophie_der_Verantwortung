
# X^∞ CapNFT – Technische Dokumentation (Proof of Concept)

## Ziel
Abbildung von Verantwortung (Cap) im X^∞-Modell als nicht-übertragbares NFT (Soulbound). CapNFT bildet Cap_Solo, Cap_Team, Cap_Potential, Rolle und Zeitstempel in einem tokenisierten Format ab.

---

## Komponenten

### 1. CapNFT Smart Contract (CapNFT.sol)
**Sprache**: Solidity (>=0.8.19)

**Kernfunktionen**:
- `mint(address, solo, team, potential, role)`: Initiale CapNFT-Erstellung durch Core-Adresse.
- `getCapData(address)`: Abfrage der Cap-Werte einer Adresse.
- `tokenURI(uint256)`: JSON-Ausgabe der NFT-Datenstruktur (on-chain generiert).

**Soulbound Mechanik**:
- `transferFrom(...)`, `safeTransferFrom(...)`, `burn(...)`: Deaktiviert via `revert()`.

**Struktur**:
```solidity
struct CapData {
  uint256 capSolo;
  uint256 capTeam;
  uint256 capPotential;
  uint256 timestamp;
  string role;
}
```

---

### 2. Frontend: CapNFT Viewer (Web)
**Technologien**:
- React (optional), Vanilla JS (PoC)
- WalletConnect v2 (QR-Login)
- Ethers.js (Blockchain-Integration)
- TailwindCSS (X^∞ Design)

**Funktionen**:
- Verbindung via Wallet (Metamask / Mobile)
- Live-Datenanzeige der CapNFTs
- Darstellung von Cap-Werten, Rolle, Zeit
- Dynamische Wirkungskreis-Visualisierung (SVG/Canvas geplant)

---

### 3. API (optional)
**Pfad**: `/capnft/:wallet`
**Antwort** (Beispiel):
```json
{
  "tokenId": "7",
  "metadata": {
    "name": "X∞ CapNFT #7",
    "attributes": [
      { "trait_type": "Cap Solo", "value": 51 },
      { "trait_type": "Cap Team", "value": 26 },
      { "trait_type": "Cap Potential", "value": 120 },
      { "trait_type": "Rolle", "value": "Tragender" },
      { "display_type": "date", "trait_type": "Zeitstempel", "value": 1714567890 }
    ]
  }
}
```

---

## Deployment

### Goerli Deployment
- Netzwerk: Ethereum Goerli
- Tools: Remix, ethers.js, Node.js
- Scripts:
  - `CapNFT.sol` → Smart Contract
  - `deploy_capnft.js` → Deployment über CLI mit Infura

**Schritte**:
1. Kompiliere `CapNFT.sol` in Remix
2. Deploye mit deiner Core-Adresse
3. Verwende `mint()` zur Ausgabe von CapNFTs
4. Verbinde Viewer über QR (WalletConnect) oder MetaMask

---

## Sicherheit & Integrität
- Keine Transfers möglich (soulbound)
- Cap-Daten auditierbar via Blockchain
- `mint()` nur durch Core-Adresse
- Struktur erweiterbar für `CapPast`, `CapReturn`, `k_Werte` etc.

---

## Ausblick
- Integration mit CapLedger für Feedback/Strafen
- NFT-basierte Repräsentanz im vollständigen X^∞-System
- Kaskadierbare CapNFT-Strukturen möglich

---

**Status**: PoC erfolgreich abgeschlossen (Frontend, Smart Contract, API vorbereitet)

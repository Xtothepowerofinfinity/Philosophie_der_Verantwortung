
# CapTLS POC – Proof-of-Concept Design

## Ziel
Demonstration eines TLS-ähnlichen Handshakes mit Cap-Wallet als Authentifizierungsanker, ohne klassische PKI.

---

## Komponenten
- CapVPNClient (Node.js / Dart)
- CapVPNExitNode (Go / Rust)
- CapTokenVerifier (JWT-like + CapScope inspection)
- WalletSigner (MetaMask / Local Wallet key)
- TLS Overlay (using ephemeral keys)

---

## Ablauf

1. Client erzeugt:
   - Challenge `C = hash(TIME + salt)`
   - Signatur `S = sign(C, WalletPrivateKey)`
   - sendet: Wallet, CapToken, C, S

2. Server prüft:
   - Wallet-Existenz in SmartContract
   - CapToken-Signatur
   - S über C (ECDSA verify)
   - Scope: 'net:/vpn'

3. Bei Erfolg:
   - Server generiert DH-Public-Key
   - sendet + selbstsigniertes TLS-Cert (gilt nur für Sitzung)

4. Tunnel beginnt
   - Full TLS 1.3 Pipeline aktiv
   - Session key derived via shared secret (ECDH or PQ hybrid)
   - Auditlog per CapLogger

---

## Anforderungen
- Web3 Provider (Infura / Alchemy)
- eth-crypto oder web3dart
- TLS handshake over HTTPS or raw socket

---

## Sicherheit
- Forward secrecy
- No persistent identity
- Only Cap-based access

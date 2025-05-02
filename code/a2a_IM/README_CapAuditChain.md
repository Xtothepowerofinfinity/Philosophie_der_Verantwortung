
# CapAuditChain – Deployment Guide (Goerli + IPFS)

This project enables decentralized audit logging for X^∞ CapChains using:
- Solidity Smart Contract (`CapAuditStorage.sol`)
- IPFS upload via [Web3.Storage](https://web3.storage)
- Deployment/interaction script via Hardhat

---

## 📦 Contents

| File                     | Description                            |
|--------------------------|----------------------------------------|
| `CapAuditStorage.sol`    | Solidity contract to store audit meta |
| `cap_chain_audit_log.json` | Full audit data (SHA256 hashed)      |
| `deploy_audit.js`        | Node script to hash, upload, deploy    |

---

## 🚀 Requirements

- Node.js + NPM
- [Hardhat](https://hardhat.org)
- Infura/Alchemy endpoint (Goerli)
- `web3.storage` API token

Install dependencies:

```bash
npm install --save-dev hardhat ethers web3.storage dotenv
```

---

## 🔐 Environment (.env)

```
WEB3_STORAGE_TOKEN=your_web3_storage_token
```

---

## 📂 Usage

### 1. Prepare your audit log

Ensure your audit log is saved as:
```bash
cap_chain_audit_log.json
```

Example structure:
```json
{
  "cap_id": "Z-001",
  "verifications": {
    "chain_integrity": { "valid": true }
  },
  "cap_chain_snapshot": { ... }
}
```

---

### 2. Compile & deploy contract

```bash
npx hardhat compile
npx hardhat run deploy_audit.js --network goerli
```

This will:
- SHA256 hash the audit log
- Upload full log to IPFS
- Deploy the contract
- Store hash + IPFS ref on Goerli chain

---

## 🔗 Example TX Output

```
📦 IPFS Hash: Qm123...
🔐 Audit Hash: 0xabc123...
✅ Contract deployed to: 0x123...
📝 Audit record stored.
```

---

## 📡 Verifying Audit On-Chain

```solidity
CapAuditStorage(records[capId])
```

Use Etherscan or direct query to verify:

- IPFS record matches expected file
- Hash integrity aligns with SHA256

---

## 🔁 Notes

- For production: replace `storeAudit()` caller with role-restricted function
- Optional: append audit verification logs to NFT metadata


# CapAuditChain v2 – Blockchain Deployment (Audits + Incidents)

This project stores Cap-based audit + incident records on-chain via:

- `CapAuditStorageV2.sol` smart contract
- IPFS upload via `web3.storage`
- Hardhat deployment script `deploy_audit_v2.js`

---

## 📁 Contents

| File                       | Description                             |
|----------------------------|-----------------------------------------|
| `CapAuditStorageV2.sol`    | Solidity contract for audit + incident  |
| `deploy_audit_v2.js`       | Node/Hardhat script for full deployment |
| `cap_chain_audit_log.json` | Example audit log                       |
| `incident_hid_record.json` | Example incident report                 |

---

## 🛠 Requirements

- Node.js & NPM
- Hardhat (`npm install --save-dev hardhat ethers web3.storage dotenv`)
- Goerli RPC (e.g. via Infura/Alchemy)
- Web3.Storage API Token

Create `.env` with:

```
WEB3_STORAGE_TOKEN=your_token_here
```

---

## 🚀 Deploy Steps

```bash
npx hardhat compile
npx hardhat run deploy_audit_v2.js --network goerli
```

The script will:

1. SHA256-hash both `audit` and `incident` JSON files
2. Upload them to IPFS
3. Deploy `CapAuditStorageV2.sol`
4. Call `storeAudit(...)` and `storeIncident(...)`

---

## ✅ Example Output

```
✅ Contract deployed to: 0x...
📦 Audit stored: Z-001
⚠️ Incident stored.
```

---

## 📡 Etherscan Verification

Use:

- `getAudit(capId)`
- `getIncident(incidentId)`

...to verify correctness and integrity of records.

---

## 🧠 Philosophy

This contract supports the X^∞ principle of **accountable impact**:
- Every delegated Cap-action must be verifiable
- Incidents must be traceable
- Storage must be immutable


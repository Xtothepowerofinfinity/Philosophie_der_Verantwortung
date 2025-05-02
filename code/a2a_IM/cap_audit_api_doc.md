
# Cap Audit API – Documentation

This API exposes audit data for CapToken-based execution chains within the X^∞ system.  
It enables inspection of delegation integrity, scope usage, and acknowledgement state.

## 🌐 Base URL

```
http://<your-host>:5000/
```

## 📥 Endpoints

### 1. `GET /audit`

Returns the full audit log, including:

- Task metadata
- Delegation chain
- Scope usage
- Acknowledgements
- Validation results

**Example Request**
```bash
curl http://localhost:5000/audit
```

**Response**
```json
{
  "status": "success",
  "audit": {
    "cap_id": "Z-001",
    "audit_timestamp": "...",
    ...
  }
}
```

---

### 2. `GET /audit/summary`

Returns a concise summary with key audit flags:

- Cap ID
- Timestamp
- Delegation valid?
- Acknowledged?
- Incident flag

**Example Request**
```bash
curl http://localhost:5000/audit/summary
```

**Response**
```json
{
  "status": "success",
  "summary": {
    "cap_id": "Z-001",
    "timestamp": "...",
    "chain_valid": true,
    "acknowledged": true,
    "incident": false
  }
}
```

---

## 📄 File Origin

Audit data is loaded from:
```
cap_chain_audit_log.json
```

Ensure this file exists in the same directory as `cap_audit_api.py`.

---

## 🧪 Usage

- Monitor execution accountability in Cap-gated environments
- Use for verification of delegation integrity
- Enables system-level auditing without human dependency

---

## 🏷 Version

`CapAuditAPI v0.1` – stateless, file-driven.

For production use, integrate with CapChain database backend.

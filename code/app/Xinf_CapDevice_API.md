
# X^∞ CapDevice API – Feedback, Cap-Management, Identity Link

## Base URL
`https://api.xinf.system` (placeholder)

---

## POST /feedback/submit

Submit a feedback entry (f_E / m_E) with optional metadata.

### Request Body (JSON)
{
  "wallet": "0xabc123...",
  "type": "technical" | "social" | "systemic" | "contextual",
  "f_e": 0.8,
  "m_e": 0.1,
  "comment": "Optional comment",
  "timestamp": 1714592000,
  "context": {
    "location": "lat,long",
    "wifi_mac": "xx:xx:xx:xx:xx:xx",
    "ble_devices": ["aa:bb:cc:dd:ee:ff"],
    "rfid_uid": "0xDEADBEEF"
  }
}

### Response
200 OK
{
  "status": "received",
  "capImpact": "pending_evaluation"
}

---

## GET /cap/:wallet

Returns current Cap status of wallet.

### Response
{
  "wallet": "0xabc123...",
  "cap_solo": 51,
  "cap_team": 26,
  "cap_potential": 120,
  "role": "Projektleiter",
  "last_feedback": 1714590000
}

---

## POST /cap/authorize

Generates a CapToken for a given wallet session.

### Request Body
{
  "wallet": "0xabc123...",
  "session_token": "xyz",
  "requested_scope": ["access_gate", "open_dashboard"]
}

### Response
{
  "capToken": {
    "wallet": "0xabc123...",
    "scope": [...],
    "cap_level": 91,
    "valid_until": 1714600000,
    "signature": "0x..."
  }
}

---

## POST /identity/link

Links RFID, BLE or WiFi identity to a wallet (temporary or persistent).

### Request Body
{
  "wallet": "0xabc123...",
  "rfid_uid": "0x123456",
  "ble_mac": "aa:bb:cc:dd:ee:ff",
  "wifi_mac": "00:11:22:33:44:55"
}

### Response
{
  "status": "linked",
  "valid_until": 1714700000
}


import json
import os
import requests
import uuid
from datetime import datetime
from cap_signature_verify import verify_signature
from eth_account import Account
from eth_account.messages import encode_defunct

# Load ENV manually (or use dotenv if needed)
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "0x...")
SIGNER = Account.from_key(PRIVATE_KEY).address
CAP_ID = os.getenv("CAP_ID", "SYS-CORE")
AGENT = os.getenv("AGENT_ID", "capos.local")
VPN_ENDPOINT = os.getenv("VPN_ENDPOINT", "http://127.0.0.1:8989/gate_receive")

def detect_local_event():
    # Simulierter Trigger: nginx restart fehlgeschlagen
    return {
        "task_id": f"NGINXFAIL-{uuid.uuid4().hex[:6]}",
        "severity": "high",
        "description": "Nginx failed to restart – possible overload",
    }

def build_incident_payload(event):
    now = datetime.utcnow().isoformat() + "Z"
    msg = f"{event['task_id']}|{CAP_ID}|{AGENT}|{now}"
    signable = encode_defunct(text=msg)
    signed = Account.sign_message(signable, private_key=PRIVATE_KEY)
    return {
        "task_id": event["task_id"],
        "cap_id": CAP_ID,
        "agent": AGENT,
        "timestamp": now,
        "severity": event["severity"],
        "description": event["description"],
        "signer": SIGNER,
        "signature": signed.signature.hex()
    }

def send_to_gate(incident):
    headers = {
        "Content-Type": "application/json",
        "X-Cap-VPN": "true",
        "X-Signed-By": incident["signer"]
    }
    response = requests.post(VPN_ENDPOINT, json=incident, headers=headers)
    print(f"📡 Gate response: {response.status_code} → {response.text}")
    return response.ok

if __name__ == "__main__":
    event = detect_local_event()
    incident = build_incident_payload(event)
    send_to_gate(incident)

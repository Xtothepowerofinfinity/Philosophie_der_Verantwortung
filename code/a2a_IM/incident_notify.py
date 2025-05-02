
import json
import requests
import argparse
from cap_signature_verify import verify_signature

def notify_support(json_file, signer_address, webhook_url):
    with open(json_file, 'r') as f:
        incident = json.load(f)

    message = f"{incident['task_id']}|{incident['cap_id']}|{incident['agent']}|{incident['timestamp']}"
    signature = incident.get("signature")

    if not signature or not signer_address:
        return {"status": "invalid", "reason": "Missing signature or signer"}

    is_valid = verify_signature(message, signature, signer_address)
    if not is_valid:
        return {"status": "invalid", "reason": "Signature does not match"}

    # Construct support packet
    payload = {
        "incident_id": incident["task_id"],
        "agent": incident["agent"],
        "cap_id": incident["cap_id"],
        "severity": incident.get("severity", "normal"),
        "description": incident.get("description", ""),
        "timestamp": incident["timestamp"],
        "signer": signer_address
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=payload, headers=headers)

    return {
        "status": "notified" if response.status_code == 200 else "failed",
        "response": response.text,
        "code": response.status_code
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--signer", required=True)
    parser.add_argument("--webhook", required=True)
    args = parser.parse_args()

    result = notify_support(args.file, args.signer, args.webhook)
    print(json.dumps(result, indent=2))

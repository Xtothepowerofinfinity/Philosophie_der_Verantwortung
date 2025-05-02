
import json
from cap_signature_verify import verify_signature

def verify_incident_signature(json_file_path):
    with open(json_file_path, 'r') as f:
        incident = json.load(f)

    cap_id = incident.get("cap_id", "")
    task_id = incident.get("task_id", "")
    agent = incident.get("agent", "")
    timestamp = incident.get("timestamp", "")
    signature = incident.get("signature", "")
    expected_address = incident.get("signer", "")

    if not signature or not expected_address:
        return {"status": "invalid", "reason": "Missing signature or signer"}

    message = f"{task_id}|{cap_id}|{agent}|{timestamp}"
    valid = verify_signature(message, signature, expected_address)

    return {
        "status": "valid" if valid else "invalid",
        "message": message,
        "signer": expected_address,
        "result": valid
    }

# Beispiel:
# result = verify_incident_signature("incident_hid_record.json")
# print(result)

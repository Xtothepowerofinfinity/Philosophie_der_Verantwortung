
import json
import argparse
import requests

def send_via_capvpn(incident_file, vpn_endpoint):
    with open(incident_file, 'r') as f:
        payload = json.load(f)

    headers = {
        "Content-Type": "application/json",
        "X-Cap-VPN": "true",
        "X-Signed-By": payload.get("signer", "unknown")
    }

    response = requests.post(vpn_endpoint, json=payload, headers=headers)
    print(f"📡 Sent via CapVPN → Status: {response.status_code}")
    return response.text

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--endpoint", required=True)
    args = parser.parse_args()

    send_via_capvpn(args.file, args.endpoint)


import json
import argparse
from eth_account import Account
from eth_account.messages import encode_defunct

def sign_incident(task_id, cap_id, agent, timestamp, private_key):
    message = f"{task_id}|{cap_id}|{agent}|{timestamp}"
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key=private_key)

    return {
        "message": message,
        "signature": signed.signature.hex(),
        "signer": signed.address
    }

def sign_and_embed(input_file, output_file, private_key):
    with open(input_file, 'r') as f:
        incident = json.load(f)

    task_id = incident.get("task_id")
    cap_id = incident.get("cap_id")
    agent = incident.get("agent")
    timestamp = incident.get("timestamp")

    signed = sign_incident(task_id, cap_id, agent, timestamp, private_key)
    incident["signature"] = signed["signature"]
    incident["signer"] = signed["signer"]

    with open(output_file, 'w') as f:
        json.dump(incident, f, indent=4)

    print("✅ Incident file updated with signature.")
    return incident

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", required=True, help="Input incident JSON")
    parser.add_argument("--outfile", required=True, help="Output JSON path")
    parser.add_argument("--key", required=True, help="Private key (0x...)")
    args = parser.parse_args()

    sign_and_embed(args.infile, args.outfile, args.key)


from eth_account import Account
from eth_account.messages import encode_defunct
import json

def sign_incident(task_id, cap_id, agent, timestamp, private_key):
    message = f"{task_id}|{cap_id}|{agent}|{timestamp}"
    msg = encode_defunct(text=message)
    signed = Account.sign_message(msg, private_key=private_key)

    return {
        "message": message,
        "signature": signed.signature.hex(),
        "signer": signed.address
    }

# Beispiel für CLI-Anwendung:
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--cap", required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--ts", required=True)
    parser.add_argument("--key", required=True)
    args = parser.parse_args()

    result = sign_incident(args.task, args.cap, args.agent, args.ts, args.key)
    print(json.dumps(result, indent=2))

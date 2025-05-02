import json
import argparse
import os
from cap_signature_verify import verify_signature
from web3 import Web3
from dotenv import load_dotenv

def calculate_cap_feedback(incident, phi=1.2, psi=0.9):
    cap_potential = incident.get("cap_potential", 50)
    if cap_potential <= 0:
        cap_potential = 1

    w_e = 1 / cap_potential
    f_e = incident.get("f_e", 0.0)
    m_e = incident.get("m_e", 0.0)

    delta = phi * w_e * f_e - psi * m_e
    return round(delta, 4)

def verify_and_store(json_path, contract_address, abi_path, signer_address, rpc_url):
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("Missing PRIVATE_KEY in environment.")

    with open(json_path, 'r') as f:
        incident = json.load(f)

    message = f"{incident['task_id']}|{incident['cap_id']}|{incident['agent']}|{incident['timestamp']}"
    signature = incident.get("signature")
    expected = signer_address

    if not signature or not expected:
        raise ValueError("Missing signature or expected signer address.")

    valid = verify_signature(message, signature, expected)
    if not valid:
        raise ValueError("Invalid signature. Aborting submission.")

    # ⬇️ ΔCap Integration
    delta = calculate_cap_feedback(incident)
    incident["cap_feedback"] = delta
    print(f"🔁 ΔCap feedback: {delta}")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    with open(abi_path, 'r') as f:
        abi = json.load(f)

    contract = w3.eth.contract(address=contract_address, abi=abi)
    account = w3.eth.account.from_key(private_key)
    w3.eth.default_account = account.address

    tx = contract.functions.storeIncident(
        incident["task_id"],
        incident["cap_id"],
        incident["agent"],
        incident.get("severity", "normal"),
        w3.keccak(text=json.dumps(incident, sort_keys=True)),
        incident.get("ipfs", "N/A")
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"✅ Submitted. TX Hash: {w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--abi", required=True)
    parser.add_argument("--signer", required=True)
    parser.add_argument("--rpc", required=True)
    args = parser.parse_args()

    verify_and_store(args.file, args.contract, args.abi, args.signer, args.rpc)
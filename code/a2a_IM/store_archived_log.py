
import json
import argparse
import os
from web3 import Web3
from dotenv import load_dotenv

def store_archived_log(json_path, contract_address, abi_path, rpc_url):
    load_dotenv()
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ValueError("Missing PRIVATE_KEY in environment.")

    with open(json_path, 'r') as f:
        archive = json.load(f)

    meta = archive["metadata"]
    cap_id = meta["incident_id"] or "AUD-" + meta["audit_hash"][:6]
    audit_hash = Web3.keccak(text=json.dumps(archive["data"], sort_keys=True))
    ipfs_hash = meta.get("ipfs", "N/A")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    with open(abi_path, 'r') as f:
        abi = json.load(f)

    contract = w3.eth.contract(address=contract_address, abi=abi)
    account = w3.eth.account.from_key(private_key)
    w3.eth.default_account = account.address

    tx = contract.functions.storeAudit(
        cap_id,
        audit_hash,
        ipfs_hash
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"✅ Archived log stored. TX Hash: {w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--abi", required=True)
    parser.add_argument("--rpc", required=True)
    args = parser.parse_args()

    store_archived_log(args.file, args.contract, args.abi, args.rpc)

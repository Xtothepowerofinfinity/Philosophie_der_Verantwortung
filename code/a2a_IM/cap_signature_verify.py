
from eth_account import Account
from eth_account.messages import encode_defunct

def verify_signature(message: str, signature: str, expected_address: str) -> bool:
    try:
        msg = encode_defunct(text=message)
        signer = Account.recover_message(msg, signature=signature)
        return signer.lower() == expected_address.lower()
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

# Beispiel:
# message = "INC-001|Z-001|node-23.gate.local|2025-05-02T12:00:00Z"
# signature = "0x..."
# expected = "0xabc..."
# print(verify_signature(message, signature, expected))

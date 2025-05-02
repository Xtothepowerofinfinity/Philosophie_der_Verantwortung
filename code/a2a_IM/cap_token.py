
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature

class CapToken:
    def __init__(self, scope, issuer):
        self.scope = scope
        self.issuer = issuer
        self.issued_at = datetime.utcnow().isoformat()
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def verify_scope(self, action):
        return action in self.scope

    def sign_message(self, message: str):
        signature = self.private_key.sign(
            message.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
        r, s = decode_dss_signature(signature)
        return {
            "message": message,
            "signature": {
                "r": r,
                "s": s
            },
            "signed_by": self.issuer,
            "issued_at": self.issued_at
        }

    def export_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8")

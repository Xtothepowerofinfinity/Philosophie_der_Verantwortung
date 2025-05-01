
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from eth_account.messages import encode_defunct
from web3.auto import w3

AUDIT_LOG = "/var/log/cap_audit_log.jsonl"
PORT = 1717

def verify_signature(wallet, signature, message_hash):
    try:
        recovered = w3.eth.account.recover_message(
            encode_defunct(hexstr=message_hash),
            signature=signature
        )
        return recovered.lower() == wallet.lower()
    except:
        return False

class CapAuditHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/submit":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return

        timestamp = int(time.time())
        payload['received_at'] = timestamp

        message_fields = ['type', 'wallet', 'timestamp']
        message = '|'.join(str(payload.get(field, '')) for field in message_fields)
        message_hash = w3.keccak(text=message).hex()

        if not verify_signature(payload.get("wallet", ""), payload.get("signature", ""), message_hash):
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Signature verification failed")
            return

        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(payload) + "\n")

        if payload["type"] == "incident":
            print("!! INCIDENT: triggering chainfeed...")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    print(f"CapAuditDaemon starting on port {PORT}")
    server = HTTPServer(('', PORT), CapAuditHandler)
    server.serve_forever()

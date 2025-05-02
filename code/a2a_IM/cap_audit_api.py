
from flask import Flask, jsonify
import json

app = Flask(__name__)
AUDIT_FILE = "cap_chain_audit_log.json"

@app.route('/audit', methods=['GET'])
def get_audit_log():
    try:
        with open(AUDIT_FILE, 'r') as f:
            data = json.load(f)
        return jsonify({"status": "success", "audit": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/audit/summary', methods=['GET'])
def get_summary():
    try:
        with open(AUDIT_FILE, 'r') as f:
            data = json.load(f)
        summary = {
            "cap_id": data["cap_id"],
            "timestamp": data["audit_timestamp"],
            "chain_valid": data["verifications"]["chain_integrity"]["valid"],
            "acknowledged": data["verifications"]["acknowledgements"]["valid"],
            "incident": data["cap_chain_snapshot"]["incident_flag"]
        }
        return jsonify({"status": "success", "summary": summary}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Run with: flask run --host=0.0.0.0

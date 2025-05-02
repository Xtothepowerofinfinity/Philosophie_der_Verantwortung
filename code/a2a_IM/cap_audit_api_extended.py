
from flask import Flask, request, jsonify
import json
from datetime import datetime
import hashlib
import threading

app = Flask(__name__)

audit_log = []
alert_hooks = []

@app.route("/incident", methods=["POST"])
def receive_incident():
    data = request.get_json()
    incident_id = data.get("incident_id")
    cap_id = data.get("cap_id")
    agent = data.get("agent")
    severity = data.get("severity", "normal")
    description = data.get("description", "")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat() + "Z")

    record = {
        "incident_id": incident_id,
        "cap_id": cap_id,
        "agent": agent,
        "severity": severity,
        "description": description,
        "timestamp": timestamp,
        "audit_hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    }

    audit_log.append(record)
    print(f"📥 Incident received + logged: {incident_id}")

    if severity.lower() in ["high", "critical"]:
        for hook in alert_hooks:
            threading.Thread(target=trigger_alert, args=(hook, record)).start()

    return jsonify({"status": "received", "hash": record["audit_hash"]})

@app.route("/register_alert", methods=["POST"])
def register_alert():
    data = request.get_json()
    url = data.get("url")
    if url:
        alert_hooks.append(url)
        return jsonify({"status": "hook_registered", "url": url})
    return jsonify({"error": "no url provided"}), 400

@app.route("/audit_log", methods=["GET"])
def get_log():
    return jsonify(audit_log)

def trigger_alert(hook_url, record):
    try:
        import requests
        res = requests.post(hook_url, json=record)
        print(f"🚨 Alert sent to {hook_url} – Status: {res.status_code}")
    except Exception as e:
        print(f"⚠️ Alert error: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8787)

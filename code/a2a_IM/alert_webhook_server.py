
from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)
WEBHOOK_LOG = "webhook_alert_log.json"

@app.route('/webhook/incident', methods=['POST'])
def receive_alert():
    try:
        data = request.get_json(force=True)
        data['received_at'] = datetime.utcnow().isoformat()

        try:
            with open(WEBHOOK_LOG, 'r') as f:
                alerts = json.load(f)
        except FileNotFoundError:
            alerts = []

        alerts.append(data)
        with open(WEBHOOK_LOG, 'w') as f:
            json.dump(alerts, f, indent=4)

        return jsonify({"status": "received", "entry": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook/log', methods=['GET'])
def view_log():
    try:
        with open(WEBHOOK_LOG, 'r') as f:
            log = json.load(f)
        return jsonify(log), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Start with: flask run --host=0.0.0.0 --port=5050

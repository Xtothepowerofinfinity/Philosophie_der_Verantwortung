
import json
from datetime import datetime
from pathlib import Path

class AlertSender:
    def __init__(self, output_path="alerts_log.json"):
        self.output_path = Path(output_path)
        if not self.output_path.exists():
            with open(self.output_path, "w") as f:
                json.dump([], f)

    def send_alert(self, incident_id, message, level="alert"):
        alert = {
            "incident_id": incident_id,
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }

        with open(self.output_path, "r") as f:
            alerts = json.load(f)

        alerts.append(alert)

        with open(self.output_path, "w") as f:
            json.dump(alerts, f, indent=4)

        return alert

# Beispiel:
# sender = AlertSender()
# sender.send_alert("Z-001", "⚠️ Escalated incident due to high w_E", "alert")

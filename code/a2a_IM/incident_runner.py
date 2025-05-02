
from incident_engine_enhanced import IncidentEngine
from alert_sender import AlertSender
import json

# Lade Incident-Daten
incident_file = "incident_hid_record.json"

# Initialisiere Module
engine = IncidentEngine()
sender = AlertSender()

# Verarbeite und bewerte Incident
incident = engine.load_incident(incident_file)
evaluation = engine.evaluate_incident(incident)
alert = engine.escalate_if_needed(evaluation)

# Benachrichtigung bei Eskalation
if alert["status"] == "alert":
    sender.send_alert(
        incident_id=evaluation["incident_id"],
        message=alert["message"],
        level=alert["status"]
    )
    print(f"🚨 Alert sent: {alert['message']}")
else:
    print(f"✅ No escalation required: {alert['message']}")

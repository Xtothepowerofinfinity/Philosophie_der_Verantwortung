
import json
from datetime import datetime

class IncidentEngine:
    def __init__(self, feedback_phi=1.0, feedback_psi=0.7):
        self.incidents = []
        self.feedback_phi = feedback_phi
        self.feedback_psi = feedback_psi
        self.escalation_threshold = 0.8  # adjustable based on CapSystem rules

    def load_incident(self, json_file_path):
        with open(json_file_path, 'r') as f:
            incident = json.load(f)
            self.incidents.append(incident)
            return incident

    def compute_delta_cap_feedback(self, cap_potential, f_e, m_e):
        if cap_potential <= 0:
            cap_potential = 0.001  # prevent division by zero
        w_e = 1 / cap_potential
        delta = self.feedback_phi * w_e * f_e - self.feedback_psi * m_e
        return delta, w_e

    def evaluate_incident(self, incident):
        cap_potential = incident.get("cap_potential", 1.0)
        f_e = incident.get("feedback_score", 0.5)
        m_e = incident.get("misuse_score", 0.1)
        delta, w_e = self.compute_delta_cap_feedback(cap_potential, f_e, m_e)

        severity = "normal"
        if w_e >= self.escalation_threshold:
            severity = "escalated"

        result = {
            "delta_cap": delta,
            "w_e": w_e,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "incident_id": incident.get("task_id", "unknown")
        }
        return result

    def escalate_if_needed(self, evaluation_result):
        if evaluation_result["severity"] == "escalated":
            return {
                "status": "alert",
                "message": f"🔺 Incident {evaluation_result['incident_id']} requires escalation",
                "issued_at": evaluation_result["timestamp"]
            }
        else:
            return {
                "status": "info",
                "message": f"Incident {evaluation_result['incident_id']} within normal range",
                "issued_at": evaluation_result["timestamp"]
            }

# Beispiel:
# engine = IncidentEngine()
# inc = engine.load_incident("incident_hid_record.json")
# eval = engine.evaluate_incident(inc)
# print(engine.escalate_if_needed(eval))

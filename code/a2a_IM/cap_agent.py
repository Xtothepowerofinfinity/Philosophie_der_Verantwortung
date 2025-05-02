
import json
from datetime import datetime

class CapToken:
    def __init__(self, scope, issuer):
        self.scope = scope
        self.issuer = issuer
        self.issued_at = datetime.utcnow().isoformat()

    def verify_scope(self, action):
        return action in self.scope

class CapAgent:
    def __init__(self, agent_id, cap_token):
        self.agent_id = agent_id
        self.cap_token = cap_token

    def handle_message(self, message):
        action = message.get("action")
        if not self.cap_token.verify_scope(action):
            return self.reject_message("Scope not allowed")

        response = {
            "from": self.agent_id,
            "to": message.get("from"),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "executed",
            "action": action,
            "ack": True
        }
        return response

    def reject_message(self, reason):
        return {
            "from": self.agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "rejected",
            "reason": reason
        }

# Beispiel zur Nutzung:
# token = CapToken(scope=["audit", "read"], issuer="XINF_Core")
# agent = CapAgent("Agent_A", token)
# msg = {"from": "Agent_B", "action": "read"}
# print(agent.handle_message(msg))

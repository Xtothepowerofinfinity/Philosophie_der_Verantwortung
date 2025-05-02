
from datetime import datetime

class MessageRouter:
    def __init__(self, agent, transport):
        self.agent = agent
        self.transport = transport
        self.log = []

    def route(self, message):
        action = message.get("action")
        required_scope = message.get("required_scope", action)

        if self.agent.cap_token.verify_scope(action):
            local_response = self.agent.handle_message(message)
            self.log_event("local", message, local_response)
            return local_response
        else:
            transport_response = self.transport.send(message, required_scope)
            self.log_event("vpn", message, transport_response)
            return transport_response

    def log_event(self, path, message, response):
        self.log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "path": path,
            "message": message,
            "response": response
        })

    def get_log(self):
        return self.log

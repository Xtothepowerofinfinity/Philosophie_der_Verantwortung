
import json
from datetime import datetime

class VPNRegistry:
    def __init__(self):
        self.registered_nodes = {}

    def register_node(self, node_id, capabilities):
        self.registered_nodes[node_id] = {
            "capabilities": capabilities,
            "last_seen": datetime.utcnow().isoformat()
        }

    def resolve_route(self, required_scope):
        for node_id, info in self.registered_nodes.items():
            if required_scope in info["capabilities"]:
                return node_id
        return None

class CapVPNTransport:
    def __init__(self, registry: VPNRegistry):
        self.registry = registry

    def send(self, message, required_scope):
        target_node = self.registry.resolve_route(required_scope)
        if not target_node:
            return {"status": "error", "reason": "no node found for scope"}
        return {
            "status": "sent",
            "to": target_node,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }

# Beispiel zur Nutzung:
# registry = VPNRegistry()
# registry.register_node("Node_X", ["read", "write", "audit"])
# transport = CapVPNTransport(registry)
# msg = {"data": "Important payload"}
# print(transport.send(msg, "read"))

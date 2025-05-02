
from cap_token import CapToken
from cap_agent import CapAgent
from vpn_transport import VPNRegistry, CapVPNTransport
from message_router import MessageRouter

# Initialisiere CapToken und Agent
token = CapToken(scope=["read", "write"], issuer="Core_Xinf")
agent = CapAgent(agent_id="Agent_A", cap_token=token)

# VPN-Registry und Transport konfigurieren
registry = VPNRegistry()
registry.register_node("Node_B", capabilities=["audit", "write"])
transport = CapVPNTransport(registry)

# Router starten
router = MessageRouter(agent=agent, transport=transport)

# Eingehende Nachricht (Simuliert)
incoming_message = {
    "from": "Agent_X",
    "action": "audit",  # Agent_A hat kein 'audit' im Scope
    "required_scope": "audit",
    "payload": "Check subsystem integrity"
}

# Nachricht routen
response = router.route(incoming_message)

# Ergebnisse anzeigen
print("Routing Result:")
print(response)

print("\nRouting Log:")
for entry in router.get_log():
    print(entry)

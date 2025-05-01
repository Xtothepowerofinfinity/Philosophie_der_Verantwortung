```python
# capvpn_client_enhanced.py
# Verbessertes CapVPN Client mit Phantom Routing und Auditlogs

import json
import requests
import subprocess
import time
from web3 import Web3
import logging

# Konfiguration (aus CapVPN_Protocol.json)
VPN_SERVER = "vpn.capos.xinf"
MIN_REQUIRED_SCOPE = "net:/vpn/core"
TOKEN_LIFETIME = 600
REFRESH_INTERVAL = 300
COMMERCIAL_BRIDGE = "protonvpn"  # Platzhalter

# Blockchain und Logging
WEB3_PROVIDER = "https://rpc.ankr.com/eth"  # Ersetze mit echtem Provider
CONTRACT_ADDRESS = "0xYourContractAddress"  # Ersetze mit echtem Adresse
CONTRACT_ABI = [...]  # Ersetze mit echter ABI
LOG_FILE = "/var/log/capvpn_audit.log"

# Logging Setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# CapToken
CAP_TOKEN = {
    "wallet": "0xAAA...",
    "scope": ["net:/vpn/core"],
    "role": "infra.user",
    "cap_level": 71,
    "signature": "0x...",
    "valid_until": 1715000000
}

# Web3 Verbindung
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# CapToken validieren
def validate_cap_token(token):
    current_time = int(time.time())
    if "net:/vpn/core" not in token["scope"]:
        raise ValueError(f"Ungültiger Scope: {token['scope']}")
    if token["valid_until"] < current_time:
        raise ValueError("CapToken abgelaufen")
    response = requests.post("https://api.xinf.system/cap/validate", json=token, verify=True)
    if response.status_code != 200:
        raise ValueError("CapToken ungültig")
    return True

# Exit Node abrufen
def get_exit_node(domain="infra"):
    node_count = contract.functions.getNodeCount(domain).call()
    if node_count == 0:
        raise ValueError("Keine Exit Nodes verfügbar")
    node = contract.functions.getNode(domain, 0).call()
    return node

# VPN-Verbindung mit Phantom Routing
def connect_vpn():
    node = get_exit_node()
    bridge_config = f"{COMMERCIAL_BRIDGE}.ovpn"  # Platzhalter
    logging.info(f"Verbinde mit Exit Node: {node}, Bridge: {COMMERCIAL_BRIDGE}")
    subprocess.run(["openvpn", "--config", bridge_config, "--remote", node], check=True)

# Auditlog schreiben
def log_session():
    log_entry = {
        "timestamp": int(time.time()),
        "cap_wallet": CAP_TOKEN["wallet"],
        "scope": CAP_TOKEN["scope"],
        "role": CAP_TOKEN["role"],
        "exit_node_id": get_exit_node()
    }
    logging.info(json.dumps(log_entry))

# Hauptlogik
def main():
    try:
        validate_cap_token(CAP_TOKEN)
        log_session()  # Initiales Log
        connect_vpn()

        start_time = int(time.time())
        while True:
            elapsed = int(time.time()) - start_time
            if elapsed > TOKEN_LIFETIME:
                logging.info("CapToken abgelaufen, trenne Verbindung")
                subprocess.run(["pkill", "openvpn"], check=True)
                break
            if elapsed % REFRESH_INTERVAL == 0:
                logging.info("Revalidiere CapToken")
                validate_cap_token(CAP_TOKEN)
                log_session()
            time.sleep(1)

    except Exception as e:
        logging.error(f"Fehler: {e}")
        subprocess.run(["pkill", "openvpn"], check=True)

if __name__ == "__main__":
    main()

# Hinweise:
# - Ersetze WEB3_PROVIDER, CONTRACT_ADDRESS, CONTRACT_ABI und bridge_config mit echten Werten.
# - Integriere mit CapGate (gate_sync.dart) für Audit-Synchronisation.
# - Verwende HTTPS und sichere Schlüsselverwaltung für Produktion.
```

**Hinweise**:
- **Voraussetzungen**: Installiere `requests`, `web3.py`, OpenVPN und `logging`. Konfiguriere `bridge_config`.
- **Erweiterungen**: Füge CapGate-Synchronisation oder dynamische Bridge-Auswahl hinzu.
- **Sicherheit**: Nutze TLS für API-Calls und verschlüsselte Logs.
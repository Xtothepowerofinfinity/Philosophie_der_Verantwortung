
from typing import Dict, List

# Beispielressourcen-Datenbank
ResourceDB = {
    "srv1": {"required_cap": 1.5, "assigned_to": None},
    "db_cluster": {"required_cap": 2.0, "assigned_to": None},
    "vpn": {"required_cap": 1.0, "assigned_to": None}
}

def map_cap_to_resource(resource_id: str, actor_id: str, cap_registry: Dict[str, Dict[str, float]]) -> bool:
    if resource_id not in ResourceDB:
        raise ValueError("Ressource nicht bekannt")

    required = ResourceDB[resource_id]["required_cap"]
    current = cap_registry.get(actor_id, {}).get("Cap_Team", 0.0)

    if current >= required:
        ResourceDB[resource_id]["assigned_to"] = actor_id
        AuditLog.append(f"{datetime.utcnow().isoformat()} | CapMapper: {actor_id} mapped to {resource_id}")
        return True
    else:
        AuditLog.append(f"{datetime.utcnow().isoformat()} | CapMapper: {actor_id} failed to map {resource_id} (Cap too low)")
        return False

def remap_roles_if_unfulfilled(cap_registry: Dict[str, Dict[str, float]]):
    for res, data in ResourceDB.items():
        assigned = data["assigned_to"]
        if not assigned:
            continue
        # Prüfen: hat der Actor überhaupt noch Cap für die Ressource?
        current = cap_registry.get(assigned, {}).get("Cap_Team", 0.0)
        if current < data["required_cap"]:
            AuditLog.append(f"{datetime.utcnow().isoformat()} | CapMapper: {assigned} unassigned from {res} (Cap lost)")
            ResourceDB[res]["assigned_to"] = None

def show_resources(actor_id: str, cap_registry: Dict[str, Dict[str, float]]) -> List[str]:
    available = []
    actor_cap = cap_registry.get(actor_id, {}).get("Cap_Team", 0.0)
    for res, data in ResourceDB.items():
        if actor_cap >= data["required_cap"]:
            available.append(res)
    return available

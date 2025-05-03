
from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime
import uuid
import math

# Simuliertes CapRegistry (ersetzt später echtes Modul)
CapRegistry = {
    "A1": {"Cap_Team": 2.0, "Cap_Potential": 3.5},
    "B7": {"Cap_Team": 1.0, "Cap_Potential": 2.5}
}

AuditLog = []

@dataclass
class DelegationPetition:
    petition_id: str
    sender: str
    recipient: str
    domain: str
    action: str
    cap_estimate: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"
    audit_ref: Optional[str] = None
    k_value: Optional[float] = None

def generate_id():
    return "PET-" + str(uuid.uuid4())[:8]

def submit_delegation_petition(sender: str, recipient: str, domain: str, action: str, cap_estimate: float) -> DelegationPetition:
    if sender not in CapRegistry:
        raise ValueError("Sender unknown")

    cap_state = CapRegistry[sender]
    if cap_state["Cap_Team"] + cap_estimate > cap_state["Cap_Potential"]:
        raise ValueError("Delegation would oversteer Cap_Potential")

    CapRegistry[sender]["Cap_Team"] += cap_estimate

    petition = DelegationPetition(
        petition_id=generate_id(),
        sender=sender,
        recipient=recipient,
        domain=domain,
        action=action,
        cap_estimate=cap_estimate
    )
    AuditLog.append(f"{petition.timestamp.isoformat()} | DelegationPetition created: {petition}")
    return petition

def return_delegation(petition: DelegationPetition, reason: str) -> None:
    petition.status = "returned"
    penalty = calculate_return_penalty(petition.cap_estimate)
    CapRegistry[petition.sender]["Cap_Team"] = max(0, CapRegistry[petition.sender]["Cap_Team"] - petition.cap_estimate)
    AuditLog.append(f"{datetime.utcnow().isoformat()} | Delegation returned: {petition.petition_id} | Reason: {reason} | Penalty: {penalty:.2f}")

def calculate_return_penalty(delta_cap: float) -> float:
    # Simplified exponential penalty model
    ρ = 0.9  # escalation factor
    RS = 1.0  # reference scale
    RE = delta_cap
    return math.exp(ρ * RE / RS)

def link_to_audit(petition: DelegationPetition, audit_id: str):
    petition.status = "fulfilled"
    petition.audit_ref = audit_id
    AuditLog.append(f"{datetime.utcnow().isoformat()} | Delegation fulfilled: {petition.petition_id} → {audit_id}")

def check_oversteer(sender: str, cap_estimate: float) -> bool:
    cap_state = CapRegistry.get(sender)
    if not cap_state:
        return False
    return (cap_state["Cap_Team"] + cap_estimate) > cap_state["Cap_Potential"]

def submit_delegation_petition(sender: str, recipient: str, domain: str, action: str, cap_estimate: float) -> DelegationPetition:
    if sender not in CapRegistry:
        raise ValueError("Sender unknown")

    if check_oversteer(sender, cap_estimate):
        AuditLog.append(f"{datetime.utcnow().isoformat()} | Delegation blocked (Oversteer): {sender} tried {cap_estimate} on {action}")
        raise ValueError("Delegation would oversteer Cap_Potential – BLOCKED")

    CapRegistry[sender]["Cap_Team"] += cap_estimate

    petition = DelegationPetition(
        petition_id=generate_id(),
        sender=sender,
        recipient=recipient,
        domain=domain,
        action=action,
        cap_estimate=cap_estimate
    )
    AuditLog.append(f"{petition.timestamp.isoformat()} | DelegationPetition created: {petition}")
    return petition

import math

# Systemweite Tracker (ersetzt später persistente Struktur)
OversteerStats = {
    "system_total": 0,
    "actor_oversteers": {}
}

def perform_oversteer(oversteerer: str, target_actor: str, domain: str, action: str, cap_value: float) -> str:
    # 1. CapCheck: Darf übersteuert werden?
    cap_state = CapRegistry.get(oversteerer)
    if not cap_state:
        raise ValueError("Oversteerer unknown")

    if cap_state["Cap_Team"] + cap_value > cap_state["Cap_Potential"]:
        raise ValueError("Oversteer not possible – Cap_Potential exceeded")

    # 2. Cap wird übernommen (Verantwortung für Aufgabe)
    CapRegistry[oversteerer]["Cap_Team"] += cap_value

    # 3. Statistiken aktualisieren
    OversteerStats["system_total"] += 1
    OversteerStats["actor_oversteers"][oversteerer] = OversteerStats["actor_oversteers"].get(oversteerer, 0) + 1

    # 4. Strafe berechnen
    penalty = calculate_oversteer_penalty(oversteerer)
    AuditLog.append(f"{datetime.utcnow().isoformat()} | OVERSTEER performed by {oversteerer} on {action} → Penalty: {penalty:.2f}")

    return f"Oversteer successful. ΔCap: +{cap_value} | Penalty: {penalty:.2f}"

def calculate_oversteer_penalty(actor: str, λ: float = 1.0, γ: float = 1.2) -> float:
    SE = OversteerStats["actor_oversteers"].get(actor, 1)
    SS = OversteerStats["system_total"] or 1
    return λ * math.exp(γ * (SE / SS))

def count_returns(actor_id: str) -> int:
    return sum(
        1 for entry in AuditLog
        if "Delegation returned" in entry and actor_id in entry
    )

def get_return_ratio(actor_id: str) -> float:
    total = len([e for e in AuditLog if actor_id in e])
    returned = count_returns(actor_id)
    return returned / total if total > 0 else 0.0

def print_return_diagnostics(actor_id: str):
    count = count_returns(actor_id)
    ratio = get_return_ratio(actor_id)
    print(f"Rückgaben für {actor_id}: {count} | Return-Ratio: {ratio:.2%}")

def extract_k_values(actor_id: str) -> list:
    return [
        float(entry.split("k=")[-1])
        for entry in AuditLog
        if f"DelegationPetition created" in entry and actor_id in entry and "k=" in entry
    ]

def get_k_median(actor_id: str) -> float:
    k_values = extract_k_values(actor_id)
    if not k_values:
        return 0.0
    k_values.sort()
    n = len(k_values)
    return (k_values[n // 2] if n % 2 == 1 else (k_values[n // 2 - 1] + k_values[n // 2]) / 2)

def check_k_thresholds(actor_id: str, k_max_allowed=3.5, k_median_warn=2.5) -> str:
    k_values = extract_k_values(actor_id)
    if not k_values:
        return "Keine k-Werte vorhanden."

    k_max = max(k_values)
    k_median = get_k_median(actor_id)

    msg = f"k_median = {k_median:.2f}, k_max = {k_max:.2f} | "
    if k_max > k_max_allowed:
        msg += "⚠️ k_max überschritten – Delegationskomplexität kritisch. "
    elif k_median > k_median_warn:
        msg += "⚠️ k_median über Schwelle – Systemlast steigend."
    else:
        msg += "✓ Komplexität im Normalbereich."
    return msg

def evaluate_k_penalty(actor_id: str, action_id: str, k_aktuell: float, λ=1.0, γ=1.2) -> float:
    # Alle historischen k-Werte für dieselbe Aufgabe und Entität extrahieren
    historical_ks = []
    for entry in AuditLog:
        if "DelegationPetition created" in entry and f"actor={actor_id}" in entry and f"action={action_id}" in entry:
            if "k=" in entry:
                try:
                    k_val = float(entry.split("k=")[-1].strip().split()[0])
                    historical_ks.append(k_val)
                except:
                    continue

    if not historical_ks:
        return 0.0  # Keine Historie = keine Strafe

    historical_ks.sort()
    n = len(historical_ks)
    k_median = historical_ks[n // 2] if n % 2 == 1 else (historical_ks[n // 2 - 1] + historical_ks[n // 2]) / 2

    if k_aktuell <= k_median:
        return 0.0

    penalty = λ * math.exp(γ * (k_aktuell / k_median))
    AuditLog.append(f"{datetime.utcnow().isoformat()} | k_Penalty for {actor_id} on {action_id}: {penalty:.2f} (k={k_aktuell} vs k_median={k_median:.2f})")
    return penalty

def apply_feedback_to_cap(actor_id: str, petent_id: str, domain: str, score: int, cap_registry: dict):
    if score == 0:
        return  # keine Wirkung

    cap_potential_petent = cap_registry.get(petent_id, {}).get("Cap_Potential_" + domain, None)
    if cap_potential_petent is None or cap_potential_petent == 0:
        raise ValueError("Cap_Potential des Petenten in dieser Domäne nicht verfügbar oder null.")

    delta = score / cap_potential_petent

    past_key = "Cap_Past_" + domain
    if past_key not in cap_registry.get(actor_id, {}):
        cap_registry[actor_id][past_key] = 0.0

    cap_registry[actor_id][past_key] += delta

    AuditLog.append(
        f"{datetime.utcnow().isoformat()} | Cap_Past updated for {actor_id} in {domain}: Δ={delta:+.2f} (Score={score}, Petent CapPot={cap_potential_petent:.2f})"
    )

def evaluate_delegation_failure(sender_id: str, receiver_id: str, action_id: str, cap_registry: dict, λ=0.5, γ=0.8):
    # Audit-Eintrag suchen: Delegation von sender_id an receiver_id zu action_id mit k
    matching_delegations = [
        entry for entry in AuditLog
        if "DelegationPetition created" in entry and
           f"actor={receiver_id}" in entry and
           f"delegated_by={sender_id}" in entry and
           f"action={action_id}" in entry and
           "k=" in entry
    ]

    if not matching_delegations:
        return  # keine relevante Delegation gefunden

    for delegation in matching_delegations:
        # k extrahieren
        try:
            k_val = float(delegation.split("k=")[-1].strip().split()[0])
        except:
            continue

        # prüfen, ob Rückgabe oder Wirkung erfolgt ist
        has_returned = any(
            "Delegation returned" in e and receiver_id in e and action_id in e
            for e in AuditLog
        )
        has_effect = any(
            "ToolCall" in e and receiver_id in e and action_id in e
            for e in AuditLog
        )

        if not has_returned and not has_effect:
            # Strafe für Sender berechnen
            delta = -λ * math.exp(γ * k_val)
            past_key = "Cap_Past_" + action_id
            if past_key not in cap_registry.get(sender_id, {}):
                cap_registry[sender_id][past_key] = 0.0

            cap_registry[sender_id][past_key] += delta
            AuditLog.append(
                f"{datetime.utcnow().isoformat()} | DelegationFailurePenalty: {sender_id} loses {abs(delta):.2f} Cap_Past in {action_id} (k={k_val})"
            )

def evaluate_delegation_failure(sender_id: str, receiver_id: str, action_id: str, cap_registry: dict, θ=0.4, ξ=0.9):
    # 1. Alle Delegationen des Senders zählen (Fehlversuche = keine Wirkung, keine Rückgabe)
    all_delegations = [
        entry for entry in AuditLog
        if "DelegationPetition created" in entry and f"delegated_by={sender_id}" in entry
    ]
    R_E_delegate = 0
    for delegation in all_delegations:
        if f"action={action_id}" not in delegation or f"actor={receiver_id}" not in delegation:
            continue
        # Prüfe auf keine Rückgabe und keine Wirkung
        k_present = "k=" in delegation
        if not k_present:
            continue
        actor_has_returned = any(
            "Delegation returned" in e and receiver_id in e and action_id in e
            for e in AuditLog
        )
        actor_has_effect = any(
            "ToolCall" in e and receiver_id in e and action_id in e
            for e in AuditLog
        )
        if not actor_has_returned and not actor_has_effect:
            R_E_delegate += 1

    # 2. Systemweite Delegationen zählen
    R_S = sum(
        1 for entry in AuditLog
        if "DelegationPetition created" in entry
    ) or 1  # vermeide Division durch 0

    # 3. Strafwert berechnen
    penalty = θ * math.exp(ξ * (R_E_delegate / R_S))

    # 4. Anwenden auf Cap_Past des Senders in der Action-Domäne
    past_key = "Cap_Past_" + action_id
    if past_key not in cap_registry.get(sender_id, {}):
        cap_registry[sender_id][past_key] = 0.0
    cap_registry[sender_id][past_key] -= penalty

    AuditLog.append(
        f"{datetime.utcnow().isoformat()} | DelegationPenalty (Doc-based): {sender_id} loses {penalty:.2f} Cap_Past in {action_id} "
        f"(R_E_delegate={R_E_delegate}, R_S={R_S}, θ={θ}, ξ={ξ})"
    )

def handle_oversteer(oversteerer_id: str, oversteered_id: str, delegator_id: str, domain: str, cap_registry: dict, λ=0.8, γ=1.1, κ=0.5):
    # Prüfe CapPotential von B
    cap_pot_B = cap_registry.get(oversteered_id, {}).get("Cap_Potential_" + domain, 0.0)
    cap_active_B = cap_registry.get(oversteered_id, {}).get("Cap_Active_" + domain, 0.0)

    if cap_pot_B >= cap_active_B:
        AuditLog.append(f"{datetime.utcnow().isoformat()} | No Oversteer: {oversteered_id} could handle task in {domain} (CapPotential sufficient).")
        return  # Keine Übersteuerung nötig

    # Prüfe ob A genug CapPotential hat
    cap_pot_A = cap_registry.get(oversteerer_id, {}).get("Cap_Potential_" + domain, 0.0)
    if cap_pot_A < cap_active_B:
        raise PermissionError("Oversteerer has insufficient CapPotential to take over.")

    # 1. CapAktiv von B temporär an A übertragen
    cap_registry[oversteerer_id]["Cap_Active_" + domain] = cap_registry[oversteerer_id].get("Cap_Active_" + domain, 0.0) + cap_active_B
    AuditLog.append(f"{datetime.utcnow().isoformat()} | Cap_Active from {oversteered_id} transferred to {oversteerer_id} in {domain}: {cap_active_B:.2f}")

    # 2. SE: Anzahl Übersteuerungen von A
    SE = sum(1 for e in AuditLog if "Oversteer" in e and oversteerer_id in e and domain in e)

    # 3. SS: Systemweite Anzahl Substitutionsaktionen (Annahmen: alle "Oversteer"-Ereignisse)
    SS = max(1, sum(1 for e in AuditLog if "Oversteer" in e and domain in e))  # ≥1

    # 4. Strafe berechnen für A
    penalty_A = λ * math.exp(γ * (SE / SS))
    cap_registry[oversteerer_id]["Cap_Past_" + domain] = cap_registry[oversteerer_id].get("Cap_Past_" + domain, 0.0) - penalty_A

    # 5. Strafe für C (halbe Strafe), außer wenn UdU
    if delegator_id != "UdU":
        penalty_C = 0.5 * penalty_A
        cap_registry[delegator_id]["Cap_Past_" + domain] = cap_registry[delegator_id].get("Cap_Past_" + domain, 0.0) - penalty_C
    else:
        penalty_C = 0.0

    # 6. Cap_Past-Kompensation für B
    compensation_B = κ * cap_active_B
    cap_registry[oversteered_id]["Cap_Past_" + domain] = cap_registry[oversteered_id].get("Cap_Past_" + domain, 0.0) + compensation_B

    # 7. Audit
    AuditLog.append(f"{datetime.utcnow().isoformat()} | Oversteer executed: {oversteerer_id} over {oversteered_id} in {domain}. "
                    f"Penalty A={penalty_A:.2f}, Penalty C={penalty_C:.2f}, Compensation B={compensation_B:.2f}.")

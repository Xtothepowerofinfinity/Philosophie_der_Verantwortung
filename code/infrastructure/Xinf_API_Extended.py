
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import math

app = FastAPI()

# --- Datenbanken / Registry ---

AuditLog = []
CapPetitions = {}
cap_registry = {}

# --- Modelle ---

class PetitionInput(BaseModel):
    petition_id: str
    description: str
    petitioner: str
    domain: str

class FeedbackInput(BaseModel):
    petition_id: str
    actor_id: str
    score: int

class DelegationInput(BaseModel):
    sender_id: str
    receiver_id: str
    domain: str
    action_id: str
    k: float

class OversteerInput(BaseModel):
    oversteerer_id: str
    oversteered_id: str
    delegator_id: str
    domain: str

# --- Petition erstellen ---
@app.post("/petition/create")
def create_petition(petition: PetitionInput):
    CapPetitions[petition.petition_id] = petition
    AuditLog.append(f"{datetime.utcnow().isoformat()} | CapPetition created: {petition.petition_id} by {petition.petitioner} in {petition.domain}")
    return {"status": "ok", "petition_id": petition.petition_id}

# --- Feedback abgeben ---
@app.post("/petition/feedback")
def petition_feedback(data: FeedbackInput):
    petition = CapPetitions.get(data.petition_id)
    if not petition:
        raise HTTPException(status_code=404, detail="Petition not found.")
    from math import tanh
    cap_pot = cap_registry.get(petition.petitioner, {}).get("Cap_Potential_" + petition.domain, 1)
    delta = data.score / cap_pot
    cap_registry[data.actor_id]["Cap_Past_" + petition.domain] = cap_registry.get(data.actor_id, {}).get("Cap_Past_" + petition.domain, 0.0) + delta
    AuditLog.append(f"{datetime.utcnow().isoformat()} | Feedback: {data.actor_id} rated Petition {data.petition_id} with {data.score:+d}")
    return {"status": "ok", "cap_delta": delta}

# --- Delegation ---
@app.post("/delegate")
def delegate_task(data: DelegationInput):
    AuditLog.append(f"{datetime.utcnow().isoformat()} | DelegationPetition created: actor={data.receiver_id} delegated_by={data.sender_id} action={data.action_id} k={data.k}")
    return {"status": "delegated", "k": data.k}

# --- Übersteuerung ---
@app.post("/oversteer")
def oversteer(data: OversteerInput):
    from math import exp
    λ = 0.8
    γ = 1.1
    κ = 0.5
    # CapCheck
    cap_pot_B = cap_registry.get(data.oversteered_id, {}).get("Cap_Potential_" + data.domain, 0)
    cap_akt_B = cap_registry.get(data.oversteered_id, {}).get("Cap_Active_" + data.domain, 0)
    if cap_pot_B >= cap_akt_B:
        return {"status": "no oversteer needed"}
    cap_pot_A = cap_registry.get(data.oversteerer_id, {}).get("Cap_Potential_" + data.domain, 0)
    if cap_pot_A < cap_akt_B:
        raise HTTPException(status_code=403, detail="CapPotential too low for oversteer.")
    # Transfer + Strafe + Kompensation
    cap_registry[data.oversteerer_id]["Cap_Active_" + data.domain] = cap_registry[data.oversteerer_id].get("Cap_Active_" + data.domain, 0) + cap_akt_B
    SE = sum(1 for e in AuditLog if "Oversteer" in e and data.oversteerer_id in e and data.domain in e)
    SS = max(1, sum(1 for e in AuditLog if "Oversteer" in e and data.domain in e))
    penalty_A = λ * exp(γ * (SE / SS))
    cap_registry[data.oversteerer_id]["Cap_Past_" + data.domain] = cap_registry[data.oversteerer_id].get("Cap_Past_" + data.domain, 0) - penalty_A
    penalty_C = 0.0
    if data.delegator_id != "UdU":
        penalty_C = 0.5 * penalty_A
        cap_registry[data.delegator_id]["Cap_Past_" + data.domain] = cap_registry[data.delegator_id].get("Cap_Past_" + data.domain, 0) - penalty_C
    compensation_B = κ * cap_akt_B
    cap_registry[data.oversteered_id]["Cap_Past_" + data.domain] = cap_registry[data.oversteered_id].get("Cap_Past_" + data.domain, 0) + compensation_B
    AuditLog.append(f"{datetime.utcnow().isoformat()} | Oversteer executed: {data.oversteerer_id} over {data.oversteered_id} in {data.domain}. Penalty A={penalty_A:.2f}, Penalty C={penalty_C:.2f}, Compensation B={compensation_B:.2f}.")
    return {"status": "oversteer complete"}

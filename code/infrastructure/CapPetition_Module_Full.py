
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import uuid

PetitionArchive = []
AuditLinks = []

@dataclass
class CapPetition:
    petition_id: str
    petitioner: str
    domain: str
    description: str
    supporters: List[str]
    priority_score: Optional[float] = None
    status: str = "open"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    audit_ref: Optional[str] = None

def generate_id():
    return "WZ-" + str(uuid.uuid4())[:8]

def submit_cap_petition(petitioner: str, domain: str, description: str, supporters: Optional[List[str]] = None) -> CapPetition:
    if supporters is None:
        supporters = []

    petition = CapPetition(
        petition_id=generate_id(),
        petitioner=petitioner,
        domain=domain,
        description=description,
        supporters=supporters
    )
    PetitionArchive.append(petition)
    return petition

def calculate_priority(petition: CapPetition, CapPotentials: dict) -> float:
    w_e_values = []
    for supporter in petition.supporters:
        cp = CapPotentials.get(supporter, 1.0)
        w_e = 1 / cp if cp != 0 else 1.0
        w_e_values.append(w_e)

    if w_e_values:
        priority = len(w_e_values) * sum(w_e_values) / len(w_e_values)
    else:
        priority = 1.0  # Default minimal priority

    petition.priority_score = priority
    return priority

def link_cap_petition_to_audit(petition: CapPetition, audit_id: str):
    petition.status = "fulfilled"
    petition.audit_ref = audit_id
    AuditLinks.append((petition.petition_id, audit_id))

# Zentrale Feedback-Datenbank (für Score-Effekt)
FeedbackDB = {}

def is_actor_allowed_to_score(actor_id: str, petition: CapPetition, responsibility_net: list, fulfilled: bool) -> bool:
    if actor_id in responsibility_net:
        return False
    if fulfilled:
        return True
    return True if not fulfilled and -10 else False

def submit_petition_feedback(actor_id: str, petition: CapPetition, score: int, responsibility_net: list):
    if score < -10 or score > 10:
        raise ValueError("Score must be between -10 and 10.")

    fulfilled = petition.status == "fulfilled"
    if not is_actor_allowed_to_score(actor_id, petition, responsibility_net, fulfilled):
        raise PermissionError("Actor is not allowed to submit feedback on this petition.")

    if petition.petition_id not in FeedbackDB:
        FeedbackDB[petition.petition_id] = {}

    FeedbackDB[petition.petition_id][actor_id] = score
    AuditLog.append(f"{datetime.utcnow().isoformat()} | Feedback: {actor_id} rated Petition {petition.petition_id} with {score:+d}")

def has_petenter_rated(petition: CapPetition) -> bool:
    ratings = FeedbackDB.get(petition.petition_id, {})
    return petition.petitioner in ratings

def enforce_petenter_feedback(petition: CapPetition):
    if petition.status == "fulfilled" and not has_petenter_rated(petition):
        AuditLog.append(f"{datetime.utcnow().isoformat()} | ⚠️ Petent {petition.petitioner} has NOT rated Petition {petition.petition_id} (mandatory)")

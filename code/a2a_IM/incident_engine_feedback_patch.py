# ⬇️ NEU: Cap-Rückkopplung basierend auf Feedback im Incident
def calculate_cap_feedback(incident, phi=1.2, psi=0.9):
    cap_potential = incident.get("cap_potential", 50)
    if cap_potential <= 0:
        cap_potential = 1

    w_e = 1 / cap_potential
    f_e = incident.get("f_e", 0.0)
    m_e = incident.get("m_e", 0.0)

    delta = phi * w_e * f_e - psi * m_e
    return round(delta, 4)

# ⬇️ Integration im Incident-Handling-Flow
def handle_incident(incident_json):
    with open(incident_json, 'r') as f:
        incident = json.load(f)

    # Signaturprüfung ausgelassen, simuliert gültig
    cap_id = incident["cap_id"]
    delta = calculate_cap_feedback(incident)
    incident["cap_feedback"] = delta

    print(f"🔁 ΔCap for {cap_id}: {delta}")
    # Weiterverarbeitung z.B. storeAudit, notifySupport ...

# xinf_full_core_deep.py – Vollintegration von X^∞ Core-, Advanced- und Deep-Modulen

from xinf_core_v2 import CapSystem, DelegationRule, CapTracker
from xinf_advanced_modules import CapPastV2, PenaltyResolver, FeedbackAnalyzer, InputResolver
from xinf_deep_cap import DeepCapPast, DeepPenalty, DeepFeedback, DeepContext
from datetime import datetime

def simulate_full_cycle():
    # Initialisiere CapSystem
    cap_sys = CapSystem(cap_solo=50, cap_team=30, cap_potential=120, cap_team_max=60)
    print(f"Initial Cap Total: {cap_sys.total_cap()}")

    # Tiefe Feedbackanalyse
    dfb = DeepFeedback()
    dfb.add_entry("tool", f_e=0.8, m_e=0.1, weight=1.2)
    dfb.add_entry("peer", f_e=0.6, m_e=0.2, weight=0.9)
    w_e, f_avg, m_avg = dfb.compute_weighted_feedback(cap_sys.cap_potential)
    cap_sys.apply_weighted_feedback(phi=1.0, psi=0.7, w_e=w_e, f_e=f_avg, m_e=m_avg)
    print(f"Cap nach Feedback: {cap_sys.total_cap()}")

    # Kontext: Vulnerabilität, Kultur, Risiko
    ctx = DeepContext(vulnerability=0.25, cultural_factor=0.85, mission_risk=1.1)

    # k-Wert & Straflogik
    k_aktuell = DelegationRule.calculate_k_value(4, [1.0, 1.1, 0.9, 1.05])
    k_penalty = DeepPenalty.penalty_k(k_aktuell, k_median=1.0, omega=2.5, chi=1.0, context_weight=ctx.adjust(1))
    cap_sys.apply_penalty(type_="complexity", severity=k_penalty)
    print(f"Cap nach k-Strafe: {cap_sys.total_cap()}")

    # Historische Cap-Aufzeichnung mit Zeitverlauf
    dcp = DeepCapPast()
    dcp.add_record("P01", value=22, delta_return=4, d_hist=3, decay_factor=0.5, timestamp="2023-06-01")
    dcp.add_record("P02", value=15, delta_return=2, d_hist=1, decay_factor=0.4, timestamp="2024-03-15")
    total_past = dcp.calculate_total(current_time=datetime.strptime("2025-05-01", "%Y-%m-%d"))
    print(f"Berechnetes Deep CapPast: {total_past}")

if __name__ == "__main__":
    simulate_full_cycle()

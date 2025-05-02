
# xinf_full_core.py – Vollständig gekoppeltes X^∞-System mit Core- und Advanced-Modulen

from xinf_core_v2 import CapSystem, DelegationRule, CapPast, Singularitaet, Kontrolle, PotenzialMatrix, Teilhabe, CapTracker
from xinf_advanced_modules import CapPastV2, PenaltyResolver, FeedbackAnalyzer, InputResolver

# Beispielhafter Systemablauf
def simulate_responsibility_cycle():
    # Init: Basis-CapSystem
    cap_sys = CapSystem(cap_solo=40, cap_team=20, cap_potential=100, cap_team_max=50)
    print(f"Initial Cap total: {cap_sys.total_cap()}")

    # Feedback-Phase
    feedback = FeedbackAnalyzer()
    feedback.add_feedback("tool", f_e=0.7, m_e=0.1)
    feedback.add_feedback("peer", f_e=0.6, m_e=0.2)
    w_e, f_avg, m_avg = feedback.calculate_weighted_feedback(cap_sys.cap_potential)
    cap_sys.apply_weighted_feedback(phi=1.2, psi=0.8, w_e=w_e, f_e=f_avg, m_e=m_avg)
    print(f"Cap after feedback: {cap_sys.total_cap()}")

    # Delegation und k-Berechnung
    k_val = DelegationRule.calculate_k_value(3, [1.1, 1.2, 0.9])
    print(f"k_aktuell: {k_val}")

    # Straflogik bei Komplexitätsüberschreitung
    penalty = PenaltyResolver.apply_penalty_k(k_aktuell=k_val, k_median=1.0, omega=3.0, chi=1.1)
    cap_sys.apply_penalty(type_="complexity", severity=penalty)
    print(f"Cap after penalty: {cap_sys.total_cap()}")

    # Historische Cap-Verwaltung
    cap_past = CapPastV2()
    cap_past.add_record("A1", value=20, delta_return=4, d_hist=3, timestamp="2025-05-01")
    print(f"CapPast total: {cap_past.calculate_total()}")

    # Kontextanpassung
    context = InputResolver(vulnerability=0.3, cultural_factor=0.85)
    adjusted_penalty = context.modulate_penalty(penalty)
    print(f"Adjusted penalty after context modulation: {adjusted_penalty}")

if __name__ == "__main__":
    simulate_responsibility_cycle()

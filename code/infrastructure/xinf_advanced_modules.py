
# xinf_advanced_modules.py – Erweiterung der Cap-Logik, Strafen, Feedback, Kontext

import math

class CapPastV2:
    def __init__(self):
        self.records = []  # List of dicts: Aj_ID, value, delta_return, D_hist, timestamp

    def add_record(self, aj_id, value, delta_return, d_hist, timestamp):
        self.records.append({
            "aj_id": aj_id,
            "value": value,
            "delta_return": delta_return,
            "d_hist": d_hist,
            "timestamp": timestamp
        })

    def calculate_total(self):
        total = 0
        for r in self.records:
            compensation = r["delta_return"] / max(r["d_hist"], 1)
            total += r["value"] + compensation
        return total

class PenaltyResolver:
    @staticmethod
    def apply_penalty_delegate(eta_E, eta_S, nu, theta):
        ratio = eta_E / max(eta_S, 0.0001)
        return nu * math.exp(theta * ratio)

    @staticmethod
    def apply_penalty_k(k_aktuell, k_median, omega, chi):
        ratio = k_aktuell / max(k_median, 0.0001)
        return omega * math.exp(chi * ratio)

class FeedbackAnalyzer:
    def __init__(self):
        self.feedback_entries = []  # List of (source, f_e, m_e)

    def add_feedback(self, source, f_e, m_e):
        self.feedback_entries.append((source, f_e, m_e))

    def calculate_weighted_feedback(self, cap_potential):
        if cap_potential < 0.0001:
            cap_potential = 0.0001  # avoid division by zero
        w_e = 1 / cap_potential
        f_total = sum([entry[1] for entry in self.feedback_entries]) / len(self.feedback_entries)
        m_total = sum([entry[2] for entry in self.feedback_entries]) / len(self.feedback_entries)
        return w_e, f_total, m_total

class InputResolver:
    def __init__(self, vulnerability=0.0, cultural_factor=1.0):
        self.vulnerability = vulnerability
        self.cultural_factor = cultural_factor

    def modulate_penalty(self, raw_penalty):
        return raw_penalty * (1 + self.vulnerability) * self.cultural_factor

    def get_vulnerability_score(self, stress_level, overload_duration):
        return min(1.0, 0.5 * stress_level + 0.05 * overload_duration)

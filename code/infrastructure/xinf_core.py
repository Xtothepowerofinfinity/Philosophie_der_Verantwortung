
# xinf_core_v2.py – Erweiterte X^∞-Systemstruktur

import math

class CapSystem:
    def __init__(self, cap_solo, cap_team, cap_potential, cap_team_max):
        self.cap_solo = cap_solo
        self.cap_team = cap_team
        self.cap_potential = cap_potential
        self.cap_team_max = cap_team_max

    def total_cap(self):
        return self.cap_solo + self.cap_team

    def is_valid(self):
        return self.total_cap() <= self.cap_potential and self.cap_team <= self.cap_team_max

    def apply_weighted_feedback(self, phi, psi, w_e, f_e, m_e):
        delta = phi * w_e * f_e - psi * m_e
        self.cap_solo += delta

    def apply_penalty(self, type_, severity):
        if type_ == "delegation":
            self.cap_team -= severity
        elif type_ == "complexity":
            self.cap_solo -= severity

class DelegationRule:
    @staticmethod
    def calculate_k_value(n_delegations, weight_factors):
        return sum(weight_factors) / n_delegations if n_delegations else 0

    @staticmethod
    def check_cap_balance(sender_cap, receiver_cap_potential):
        return sender_cap > 0 and receiver_cap_potential > 0 and sender_cap >= receiver_cap_potential * 0.5

class CapPast:
    def __init__(self, cap_solo_final=0, cap_team_final=0, cap_override_final=0, cap_return=0, cap_override_given=0):
        self.cap_solo_final = cap_solo_final
        self.cap_team_final = cap_team_final
        self.cap_override_final = cap_override_final
        self.cap_return = cap_return
        self.cap_override_given = cap_override_given

    def total(self):
        return (self.cap_solo_final + self.cap_team_final +
                self.cap_override_final + self.cap_return +
                self.cap_override_given)

    def apply_penalty(self, penalty_factor):
        penalty = penalty_factor * math.exp(self.total())
        self.cap_solo_final -= penalty

class Singularitaet:
    def __init__(self, k, alpha):
        self.k = k
        self.alpha = alpha

    def dSKI_dt(self, ski):
        return self.k * ski + self.alpha * ski**2

    def blowup_time(self, t0, t):
        return 1 / (t0 - t)

class Kontrolle:
    @staticmethod
    def system_stabil(dt_c, dt_ski):
        return dt_c >= dt_ski

class PotenzialMatrix:
    def __init__(self):
        self.eintraege = []

    def add_eintrag(self, talent, freude, kompetenz):
        self.eintraege.append((talent, freude, kompetenz))

    def scharfste_wirkung(self):
        return max(self.eintraege, key=lambda x: x[2])

class Teilhabe:
    def __init__(self, cap, status='aktiv'):
        self.cap = cap
        self.status = status

    def aberkennen(self):
        self.status = 'nicht_aktiv'

    def reaktivieren(self, neue_verantwortung_getragen):
        if neue_verantwortung_getragen:
            self.status = 'aktiv'

class CapTracker:
    def __init__(self):
        self.cap_log = []

    def track(self, timestamp, cap_solo, cap_team):
        self.cap_log.append({
            "time": timestamp,
            "cap_solo": cap_solo,
            "cap_team": cap_team,
            "total": cap_solo + cap_team
        })

    def recent_change(self):
        if len(self.cap_log) >= 2:
            delta = self.cap_log[-1]["total"] - self.cap_log[-2]["total"]
            return delta
        return 0

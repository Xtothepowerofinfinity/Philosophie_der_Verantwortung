# udu_system.py - UdU (Unterster der Unteren) System Implementation
# Implementiert die theoretische UdU-Formel: UdU ≈ (X_k × S × (S-1)/S)^∞

import math
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, getcontext
from enum import Enum

# Hochpräzise Berechnungen
getcontext().prec = 50  # Erweiterte Präzision für ∞-Berechnungen

class ThreatLevel(Enum):
    """Klassifikation existenzieller Bedrohungen"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EXISTENTIAL = "existential"

@dataclass
class BlackSwanEvent:
    """Repräsentation eines Black Swan-Ereignisses"""
    event_id: str
    description: str
    threat_magnitude: Decimal  # X_k,Need
    affected_entities: int     # S
    threat_level: ThreatLevel
    timestamp: datetime = field(default_factory=datetime.utcnow)
    handled_by_udu: bool = False

class UdUCalculator:
    """Berechnung der UdU-Kapazität basierend auf theoretischer Formel"""
    
    @staticmethod
    def calculate_symbolic_capacity(threat_magnitude: Decimal, 
                                  entity_count: int,
                                  infinity_approximation: int = 1000) -> Decimal:
        """
        UdU Symbolische Kapazität:
        UdU ≈ (X_{k,Need} × S × (S-1)/S)^∞
        
        Für praktische Berechnung wird ∞ durch infinity_approximation approximiert
        """
        if threat_magnitude <= 0 or entity_count <= 1:
            return Decimal('0.0')  # Kein UdU bei keiner Bedrohung
        
        s = Decimal(str(entity_count))
        base_factor = threat_magnitude * s * ((s - Decimal('1.0')) / s)
        
        # ∞-Approximation durch hohe Potenz
        try:
            # Für sehr große Werte logarithmische Behandlung
            if base_factor > Decimal('10.0'):
                # log(a^n) = n * log(a)
                log_result = infinity_approximation * base_factor.ln()
                # Exponential-Approximation für praktische Verwendung
                if log_result > Decimal('100.0'):  # Overflow-Schutz
                    return Decimal('1e50')  # Praktisches "Unendlich"
                else:
                    return log_result.exp()
            else:
                return base_factor ** infinity_approximation
        except (OverflowError, Decimal.Overflow):
            return Decimal('1e50')  # Praktisches "Unendlich"
    
    @staticmethod
    def should_activate_udu(event: BlackSwanEvent, 
                           system_capacity: Decimal,
                           activation_threshold: Decimal = Decimal('0.8')) -> bool:
        """
        Entscheidet ob UdU aktiviert werden muss
        """
        if event.threat_level == ThreatLevel.EXISTENTIAL:
            return True
        
        required_capacity = UdUCalculator.calculate_symbolic_capacity(
            event.threat_magnitude, event.affected_entities
        )
        
        capacity_ratio = required_capacity / max(system_capacity, Decimal('1.0'))
        
        return capacity_ratio > activation_threshold

@dataclass 
class UdUAction:
    """UdU-Handlung ohne formale Petition"""
    action_id: str
    event: BlackSwanEvent
    action_description: str
    resources_mobilized: Decimal
    timestamp: datetime = field(default_factory=datetime.utcnow)
    effectiveness: Optional[Decimal] = None

class UdUSystem:
    """Zentrales UdU-System für Letztverantwortung"""
    
    def __init__(self):
        self.active_events: List[BlackSwanEvent] = []
        self.udu_actions: List[UdUAction] = []
        self.system_capacity_history: List[Tuple[datetime, Decimal]] = []
    
    def register_potential_threat(self, event: BlackSwanEvent) -> bool:
        """
        Registriert potenzielle existenzielle Bedrohung
        """
        self.active_events.append(event)
        
        # UdU-Aktivierung prüfen
        current_system_capacity = self._get_current_system_capacity()
        
        should_activate = UdUCalculator.should_activate_udu(
            event, current_system_capacity
        )
        
        if should_activate:
            return self._activate_udu_response(event)
        
        return False
    
    def _activate_udu_response(self, event: BlackSwanEvent) -> bool:
        """
        Aktiviert UdU-Antwort ohne formale Petition
        """
        # UdU-Kapazität berechnen
        udu_capacity = UdUCalculator.calculate_symbolic_capacity(
            event.threat_magnitude, event.affected_entities
        )
        
        # UdU-Handlung erstellen
        action = UdUAction(
            action_id=f"UdU-{event.event_id}-{datetime.utcnow().timestamp()}",
            event=event,
            action_description=f"Emergency response to {event.description}",
            resources_mobilized=min(udu_capacity, Decimal('1e10'))  # Praktisches Limit
        )
        
        self.udu_actions.append(action)
        event.handled_by_udu = True
        
        return True
    
    def _get_current_system_capacity(self) -> Decimal:
        """
        Schätzt aktuelle Systemkapazität
        """
        if not self.system_capacity_history:
            return Decimal('100.0')  # Default-Annahme
        
        return self.system_capacity_history[-1][1]
    
    def update_system_capacity(self, new_capacity: Decimal):
        """
        Aktualisiert Systemkapazitäts-Tracking
        """
        self.system_capacity_history.append((datetime.utcnow(), new_capacity))
    
    def evaluate_udu_effectiveness(self, action_id: str, 
                                  post_action_threat: Decimal) -> Decimal:
        """
        Bewertet Effektivität einer UdU-Handlung (ex-post Feedback)
        """
        action = next((a for a in self.udu_actions if a.action_id == action_id), None)
        if not action:
            return Decimal('0.0')
        
        original_threat = action.event.threat_magnitude
        threat_reduction = original_threat - post_action_threat
        
        effectiveness = threat_reduction / original_threat if original_threat > 0 else Decimal('0.0')
        action.effectiveness = max(Decimal('0.0'), min(Decimal('1.0'), effectiveness))
        
        return action.effectiveness
    
    def get_udu_status_report(self) -> Dict:
        """
        Generiert Status-Bericht des UdU-Systems
        """
        active_threats = [e for e in self.active_events if not e.handled_by_udu]
        handled_threats = [e for e in self.active_events if e.handled_by_udu]
        
        total_capacity_deployed = sum(a.resources_mobilized for a in self.udu_actions)
        
        avg_effectiveness = Decimal('0.0')
        effective_actions = [a for a in self.udu_actions if a.effectiveness is not None]
        if effective_actions:
            avg_effectiveness = sum(a.effectiveness for a in effective_actions) / len(effective_actions)
        
        return {
            "active_threats": len(active_threats),
            "handled_threats": len(handled_threats),
            "total_udu_actions": len(self.udu_actions),
            "total_capacity_deployed": str(total_capacity_deployed),
            "average_effectiveness": str(avg_effectiveness),
            "current_system_capacity": str(self._get_current_system_capacity()),
            "recent_events": [
                {
                    "event_id": e.event_id,
                    "description": e.description,
                    "threat_level": e.threat_level.value,
                    "handled": e.handled_by_udu
                }
                for e in self.active_events[-5:]  # Letzte 5 Events
            ]
        }

class UdUIntegration:
    """Integration des UdU-Systems in X^∞-Gesamtarchitektur"""
    
    def __init__(self, udu_system: UdUSystem):
        self.udu_system = udu_system
    
    def monitor_system_stability(self, entities: List, domains: List[str]) -> bool:
        """
        Überwacht Systemstabilität für potenzielle UdU-Aktivierung
        """
        # Vereinfachte Stabilitätsprüfung
        # In Realität: Komplexe Systemmetriken
        
        total_entities = len(entities)
        system_stress_indicators = []
        
        for domain in domains:
            # Beispiel-Metriken (zu erweitern)
            domain_capacity = sum(
                getattr(entity, 'get_cap_potential', lambda d: Decimal('1.0'))(domain) 
                for entity in entities
            )
            
            if domain_capacity < Decimal(str(total_entities * 0.5)):  # Kritische Schwelle
                threat_event = BlackSwanEvent(
                    event_id=f"STABILITY-{domain}-{datetime.utcnow().timestamp()}",
                    description=f"System capacity critically low in domain {domain}",
                    threat_magnitude=Decimal(str(total_entities)) - domain_capacity,
                    affected_entities=total_entities,
                    threat_level=ThreatLevel.HIGH
                )
                
                activated = self.udu_system.register_potential_threat(threat_event)
                if activated:
                    return True
        
        return False

# Demonstration und Tests
def demonstrate_udu_system():
    """Demonstration des UdU-Systems"""
    
    udu_system = UdUSystem()
    
    # Black Swan Event simulieren
    crisis_event = BlackSwanEvent(
        event_id="CRISIS-001",
        description="Massive system failure affecting 80% of entities",
        threat_magnitude=Decimal('1000.0'),
        affected_entities=100,
        threat_level=ThreatLevel.EXISTENTIAL
    )
    
    print("=== UdU System Demonstration ===")
    print(f"Crisis Event: {crisis_event.description}")
    print(f"Threat Magnitude: {crisis_event.threat_magnitude}")
    print(f"Affected Entities: {crisis_event.affected_entities}")
    
    # UdU-Kapazität berechnen
    udu_capacity = UdUCalculator.calculate_symbolic_capacity(
        crisis_event.threat_magnitude, crisis_event.affected_entities
    )
    print(f"Calculated UdU Capacity: {udu_capacity}")
    
    # System-Kapazität setzen
    udu_system.update_system_capacity(Decimal('500.0'))
    
    # Event registrieren (automatische UdU-Aktivierung)
    activated = udu_system.register_potential_threat(crisis_event)
    print(f"UdU Activated: {activated}")
    
    # Status-Bericht
    status = udu_system.get_udu_status_report()
    print(f"\nUdU Status Report:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Effektivität bewerten (simuliert)
    if udu_system.udu_actions:
        action_id = udu_system.udu_actions[0].action_id
        effectiveness = udu_system.evaluate_udu_effectiveness(
            action_id, Decimal('200.0')  # Reduzierte Bedrohung
        )
        print(f"\nUdU Action Effectiveness: {effectiveness}")

if __name__ == "__main__":
    demonstrate_udu_system()
# xinf_core_v3.py - Theoretisch konsistente X^∞-Implementierung
# Basiert auf "Physics of Symbiotic Being" - Vollständige Formel-Integration

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, getcontext

# Hochpräzise Berechnungen für Cap-Werte
getcontext().prec = 28

@dataclass
class Entity:
    """Repräsentiert eine X^∞-Entität mit allen Cap-Komponenten"""
    entity_id: str
    cap_base: Decimal = Decimal('1.0')  # Unveräußerliche Grundbefugnis
    cap_bge: Decimal = Decimal('0.0')   # BGE-Komponente
    cap_past_components: Dict[str, Decimal] = field(default_factory=dict)  # Domain-spezifische Cap_Past
    active_tasks: Dict[str, Decimal] = field(default_factory=dict)  # Aktuell übernommene Aufgaben
    
    def get_cap_potential(self, domain: str, timestamp: datetime = None) -> Decimal:
        """
        Theoretisch korrekte Cap_Potential-Berechnung:
        Cap_Potential(E,D,t) = Δ_{t-1} + Cap_BGE + Cap_Base
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Δ_{t-1} = historische Wirkung in dieser Domain
        delta_past = self.cap_past_components.get(domain, Decimal('0.0'))
        
        # Vollständige Formel
        cap_potential = delta_past + self.cap_bge + self.cap_base
        
        return max(cap_potential, Decimal('0.0'))  # Niemals negativ

@dataclass
class SystemState:
    """Globaler Systemzustand für L-Faktor-Berechnung"""
    completed_tasks: List[Tuple[str, Decimal]] = field(default_factory=list)  # (task_id, value)
    total_effects: List[Decimal] = field(default_factory=list)  # Alle Δ-Werte
    
    def calculate_l_factor(self) -> Decimal:
        """
        Systemeffizienz-Quotient L:
        L = Σ(Wert aller abgeschlossenen Aufgaben X_A) / Σ(Wert der Gesamtwirkung Δ)
        """
        if not self.completed_tasks or not self.total_effects:
            return Decimal('1.0')  # Neutral bei fehlenden Daten
        
        task_values_sum = sum(value for _, value in self.completed_tasks)
        effects_sum = sum(self.total_effects)
        
        if effects_sum == 0:
            return Decimal('1.0')
        
        return task_values_sum / effects_sum

class FeedbackWeighting:
    """Theoretisch korrekte Feedback-Gewichtung"""
    
    @staticmethod
    def calculate_w_e(entity: Entity, domain: str) -> Decimal:
        """
        Korrekte w_E-Berechnung:
        w_{E'} = 1/max(1, Cap_Potential(E'))
        """
        cap_potential = entity.get_cap_potential(domain)
        return Decimal('1.0') / max(Decimal('1.0'), cap_potential)
    
    @staticmethod
    def calculate_subjective_feedback(feedback_entries: List[Tuple[Entity, str, Decimal]], 
                                    domain: str) -> Decimal:
        """
        Subjektive Feedback-Aggregation:
        Δ = Σ_{E' ∈ S_{fb,k}} (f_{E'k} × w_{E'})
        """
        if not feedback_entries:
            return Decimal('0.0')
        
        weighted_sum = Decimal('0.0')
        for feedback_entity, _, feedback_value in feedback_entries:
            w_e = FeedbackWeighting.calculate_w_e(feedback_entity, domain)
            weighted_sum += feedback_value * w_e
        
        return weighted_sum

class CapPotentialProcessor:
    """Hauptklasse für Cap-Potential-Anpassungen"""
    
    def __init__(self, system_state: SystemState):
        self.system_state = system_state
    
    def apply_effect_to_cap_potential(self, entity: Entity, domain: str, 
                                    raw_effect: Decimal) -> Decimal:
        """
        Theoretisch korrekte Δ-Anwendung mit L-Faktor:
        ΔCap_Potential(E,D) = L·Δ (wenn Δ > 0) oder (1/L)·Δ (wenn Δ < 0)
        """
        l_factor = self.system_state.calculate_l_factor()
        
        if raw_effect > 0:
            adjusted_effect = l_factor * raw_effect
        elif raw_effect < 0:
            adjusted_effect = raw_effect / l_factor
        else:
            adjusted_effect = Decimal('0.0')
        
        # Auf Cap_Past anwenden
        current_past = entity.cap_past_components.get(domain, Decimal('0.0'))
        entity.cap_past_components[domain] = current_past + adjusted_effect
        
        # Systemstate aktualisieren
        self.system_state.total_effects.append(adjusted_effect)
        
        return adjusted_effect

class PetitionPriority:
    """Theoretisch korrekte Petition-Prioritätsberechnung"""
    
    @staticmethod
    def calculate_initial_priority(petitioner: Entity, domain: str) -> Decimal:
        """
        Korrekte Prioritätsberechnung:
        Priority_initial,X_A = w_{E'} des Petitioners
        """
        return FeedbackWeighting.calculate_w_e(petitioner, domain)
    
    @staticmethod
    def calculate_petition_score(supporters: List[Entity], domain: str) -> Decimal:
        """
        Gewichteter Unterstützungs-Score:
        Score = Σ(w_{E'}) für alle Unterstützer
        """
        total_score = Decimal('0.0')
        for supporter in supporters:
            w_e = FeedbackWeighting.calculate_w_e(supporter, domain)
            total_score += w_e
        
        return total_score

class TaskExecution:
    """Freiwillige Aufgabenübernahme und -ausführung"""
    
    def __init__(self, cap_processor: CapPotentialProcessor):
        self.cap_processor = cap_processor
    
    def adopt_task(self, entity: Entity, task_id: str, domain: str, 
                  initial_priority: Decimal) -> bool:
        """
        Aufgabenübernahme nur wenn Priority <= Cap_Potential
        """
        cap_potential = entity.get_cap_potential(domain)
        
        if initial_priority <= cap_potential:
            # Aufgabe temporär übernehmen
            entity.active_tasks[task_id] = initial_priority
            return True
        else:
            # Delegation erforderlich
            return False
    
    def complete_task(self, entity: Entity, task_id: str, domain: str,
                     feedback_entries: List[Tuple[Entity, str, Decimal]]) -> Decimal:
        """
        Aufgabe abschließen und Feedback verarbeiten
        """
        if task_id not in entity.active_tasks:
            raise ValueError(f"Task {task_id} not active for entity {entity.entity_id}")
        
        # Subjektives Feedback berechnen
        effect = FeedbackWeighting.calculate_subjective_feedback(feedback_entries, domain)
        
        # Mit L-Faktor auf Cap_Potential anwenden
        adjusted_effect = self.cap_processor.apply_effect_to_cap_potential(
            entity, domain, effect
        )
        
        # Aufgabe als abgeschlossen markieren
        task_value = entity.active_tasks.pop(task_id)
        self.cap_processor.system_state.completed_tasks.append((task_id, task_value))
        
        return adjusted_effect

class DelegationProcessor:
    """Kaskadiertes Delegationsmodell"""
    
    def __init__(self, cap_processor: CapPotentialProcessor):
        self.cap_processor = cap_processor
    
    def delegate_task(self, delegator: Entity, delegate: Entity, 
                     task_id: str, domain: str) -> bool:
        """
        Delegation mit temporärer Cap_Potential-Übertragung
        """
        if task_id not in delegator.active_tasks:
            return False
        
        task_priority = delegator.active_tasks[task_id]
        delegate_cap_potential = delegate.get_cap_potential(domain)
        
        if task_priority <= delegate_cap_potential:
            # Aufgabe übertragen
            delegator.active_tasks.pop(task_id)
            delegate.active_tasks[task_id] = task_priority
            
            # Temporäre Cap_Potential-Übertragung
            # (Vereinfacht: Delegate erhält Delegator's Cap_Potential)
            return True
        else:
            return False
    
    def calculate_delegation_effect(self, delegator: Entity, delegate: Entity,
                                  domain: str, task_result: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Delegationseffekte berechnen:
        - Delegator: Δ_{X_A,D} = Δ'_{X_A,U} × w_{E_U}
        - Delegate: Δ_{X_A,U} = Δ'_{X_A,U} × (1/Priority_initial,X_A)
        """
        w_delegate = FeedbackWeighting.calculate_w_e(delegate, domain)
        
        # Delegator-Effekt (verstärkt durch schwächeren Delegate)
        delegator_effect = task_result * w_delegate
        
        # Delegate-Effekt (skaliert durch Aufgabenpriorität)
        # Vereinfacht: Delegate erhält vollen Effekt
        delegate_effect = task_result
        
        return delegator_effect, delegate_effect

# Beispiel-Verwendung und Tests
def demonstrate_theoretical_consistency():
    """Demonstration der theoretischen Konsistenz"""
    
    # System initialisieren
    system_state = SystemState()
    cap_processor = CapPotentialProcessor(system_state)
    task_executor = TaskExecution(cap_processor)
    
    # Entities erstellen
    entity_a = Entity("A", cap_base=Decimal('1.0'), cap_bge=Decimal('0.5'))
    entity_b = Entity("B", cap_base=Decimal('1.0'), cap_bge=Decimal('0.2'))
    
    domain = "test_domain"
    
    # Initiale Cap_Potential-Werte
    print(f"Entity A Cap_Potential: {entity_a.get_cap_potential(domain)}")
    print(f"Entity B Cap_Potential: {entity_b.get_cap_potential(domain)}")
    
    # Feedback-Gewichtungen
    w_a = FeedbackWeighting.calculate_w_e(entity_a, domain)
    w_b = FeedbackWeighting.calculate_w_e(entity_b, domain)
    print(f"w_A: {w_a}, w_B: {w_b}")
    
    # Petition-Priorität
    priority_a = PetitionPriority.calculate_initial_priority(entity_a, domain)
    print(f"Priority A: {priority_a}")
    
    # Aufgabenübernahme
    can_adopt = task_executor.adopt_task(entity_a, "task_1", domain, priority_a)
    print(f"Can adopt task: {can_adopt}")
    
    # Feedback und Aufgabenabschluss
    feedback_entries = [
        (entity_b, "positive", Decimal('0.8')),
        (entity_a, "self_evaluation", Decimal('0.6'))
    ]
    
    if can_adopt:
        effect = task_executor.complete_task(entity_a, "task_1", domain, feedback_entries)
        print(f"Task completed with effect: {effect}")
        print(f"Updated Cap_Potential A: {entity_a.get_cap_potential(domain)}")
    
    # L-Faktor
    l_factor = system_state.calculate_l_factor()
    print(f"System L-Factor: {l_factor}")

if __name__ == "__main__":
    demonstrate_theoretical_consistency()
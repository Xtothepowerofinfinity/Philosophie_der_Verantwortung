# delegation_system_v3.py - Theoretisch konsistentes Delegation-System
# Implementiert korrekte Delegation-Formeln aus "Physics of Symbiotic Being"

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, getcontext
from enum import Enum
import uuid

from xinf_core_v3 import Entity, FeedbackWeighting, TaskExecution, CapPotentialProcessor

# Präzise Berechnungen
getcontext().prec = 28

class DelegationStatus(Enum):
    """Status einer Delegation"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXECUTING = "executing"
    COMPLETED = "completed"
    RETURNED = "returned"
    FAILED = "failed"

@dataclass
class DelegationRecord:
    """Delegation-Datensatz mit theoretischen Parametern"""
    delegation_id: str
    delegator: Entity
    delegate: Entity
    task_id: str
    domain: str
    task_description: str
    
    # Theoretische Werte
    initial_priority: Decimal
    delegated_cap_potential: Decimal
    k_value: Optional[Decimal] = None  # Komplexitätsfaktor
    
    status: DelegationStatus = DelegationStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.utcnow)
    completion_timestamp: Optional[datetime] = None
    
    # Effekt-Tracking
    delegate_effect: Optional[Decimal] = None
    delegator_effect: Optional[Decimal] = None
    
    def calculate_k_value(self, delegation_chain_length: int = 1) -> Decimal:
        """
        Berechnet k-Wert für Delegation-Komplexität
        """
        # Vereinfachte k-Berechnung (in Realität komplexer)
        base_k = self.initial_priority / max(self.delegated_cap_potential, Decimal('1.0'))
        self.k_value = base_k * Decimal(str(delegation_chain_length))
        return self.k_value

class DelegationProcessor:
    """Verarbeitet Delegationen nach theoretischen Prinzipien"""
    
    def __init__(self, cap_processor: CapPotentialProcessor):
        self.cap_processor = cap_processor
        self.delegations: Dict[str, DelegationRecord] = {}
        self.k_history: Dict[str, List[Decimal]] = {}  # entity_id -> k_values
    
    def initiate_delegation(self, delegator: Entity, delegate: Entity,
                          task_id: str, domain: str, task_description: str,
                          initial_priority: Decimal) -> Optional[str]:
        """
        Initiiert Delegation mit theoretischen Checks
        """
        # 1. Prüfung: Delegator hat ausreichend Cap_Potential
        delegator_cap = delegator.get_cap_potential(domain)
        if delegator_cap < initial_priority:
            return None  # Delegation nicht möglich
        
        # 2. Prüfung: Delegate hat ausreichend Cap_Potential
        delegate_cap = delegate.get_cap_potential(domain)
        if delegate_cap < initial_priority:
            return None  # Delegate kann Aufgabe nicht übernehmen
        
        # 3. Delegation erstellen
        delegation_id = f"DEL-{uuid.uuid4().hex[:8]}"
        
        delegation = DelegationRecord(
            delegation_id=delegation_id,
            delegator=delegator,
            delegate=delegate,
            task_id=task_id,
            domain=domain,
            task_description=task_description,
            initial_priority=initial_priority,
            delegated_cap_potential=delegator_cap  # Temporärer Transfer
        )
        
        # k-Wert berechnen
        delegation.calculate_k_value()
        
        # k-Historie aktualisieren
        if delegator.entity_id not in self.k_history:
            self.k_history[delegator.entity_id] = []
        self.k_history[delegator.entity_id].append(delegation.k_value)
        
        # Delegation registrieren
        self.delegations[delegation_id] = delegation
        
        # Temporäre Cap-Übertragung
        self._transfer_cap_temporarily(delegation)
        
        return delegation_id
    
    def _transfer_cap_temporarily(self, delegation: DelegationRecord):
        """
        Temporäre Cap_Potential-Übertragung während Delegation
        """
        # Vereinfachte Implementierung - in Realität komplexer
        delegation.delegate.active_tasks[delegation.task_id] = delegation.initial_priority
        delegation.status = DelegationStatus.ACCEPTED
    
    def complete_delegation(self, delegation_id: str, 
                          feedback_entries: List[Tuple[Entity, str, Decimal]]) -> bool:
        """
        Delegation abschließen mit theoretisch korrekten Effekt-Berechnungen
        """
        if delegation_id not in self.delegations:
            return False
        
        delegation = self.delegations[delegation_id]
        
        if delegation.status != DelegationStatus.ACCEPTED:
            return False
        
        # Subjektives Feedback berechnen
        raw_effect = self._calculate_subjective_feedback(feedback_entries, delegation.domain)
        
        # Delegation-Effekte berechnen (theoretisch korrekt)
        delegate_effect, delegator_effect = self._calculate_delegation_effects(
            delegation, raw_effect
        )
        
        # Effekte auf Cap_Potential anwenden
        self.cap_processor.apply_effect_to_cap_potential(
            delegation.delegate, delegation.domain, delegate_effect
        )
        
        self.cap_processor.apply_effect_to_cap_potential(
            delegation.delegator, delegation.domain, delegator_effect
        )
        
        # Delegation als abgeschlossen markieren
        delegation.delegate_effect = delegate_effect
        delegation.delegator_effect = delegator_effect
        delegation.status = DelegationStatus.COMPLETED
        delegation.completion_timestamp = datetime.utcnow()
        
        # Aufgabe aus aktiven Tasks entfernen
        delegation.delegate.active_tasks.pop(delegation.task_id, None)
        
        return True
    
    def _calculate_subjective_feedback(self, feedback_entries: List[Tuple[Entity, str, Decimal]], 
                                     domain: str) -> Decimal:
        """
        Berechnet subjektives Feedback mit korrekter Gewichtung
        """
        weighted_sum = Decimal('0.0')
        
        for feedback_entity, _, feedback_value in feedback_entries:
            w_e = FeedbackWeighting.calculate_w_e(feedback_entity, domain)
            weighted_sum += feedback_value * w_e
        
        return weighted_sum
    
    def _calculate_delegation_effects(self, delegation: DelegationRecord, 
                                    raw_effect: Decimal) -> Tuple[Decimal, Decimal]:
        """
        Theoretisch korrekte Delegation-Effekt-Berechnung:
        - Delegator: Δ_{X_A,D} = Δ'_{X_A,U} × w_{E_U}
        - Delegate: Δ_{X_A,U} = Δ'_{X_A,U} × (1/Priority_initial,X_A)
        """
        # w_E des Delegates berechnen
        w_delegate = FeedbackWeighting.calculate_w_e(delegation.delegate, delegation.domain)
        
        # Delegator-Effekt: Verstärkt durch schwächeren Delegate
        delegator_effect = raw_effect * w_delegate
        
        # Delegate-Effekt: Skaliert durch Aufgabenpriorität
        if delegation.initial_priority > 0:
            delegate_effect = raw_effect / delegation.initial_priority
        else:
            delegate_effect = raw_effect
        
        return delegate_effect, delegator_effect
    
    def return_delegation(self, delegation_id: str, reason: str) -> Decimal:
        """
        Delegation zurückgeben mit theoretischer Strafe
        """
        if delegation_id not in self.delegations:
            return Decimal('0.0')
        
        delegation = self.delegations[delegation_id]
        
        if delegation.status not in [DelegationStatus.ACCEPTED, DelegationStatus.EXECUTING]:
            return Decimal('0.0')
        
        # Rückgabe-Strafe berechnen
        penalty = self._calculate_return_penalty(delegation)
        
        # Strafe auf Delegator anwenden
        self.cap_processor.apply_effect_to_cap_potential(
            delegation.delegator, delegation.domain, -penalty
        )
        
        # Delegation als zurückgegeben markieren
        delegation.status = DelegationStatus.RETURNED
        delegation.completion_timestamp = datetime.utcnow()
        
        # Aufgabe aus aktiven Tasks entfernen
        delegation.delegate.active_tasks.pop(delegation.task_id, None)
        
        return penalty
    
    def _calculate_return_penalty(self, delegation: DelegationRecord) -> Decimal:
        """
        Berechnet Strafe für Delegation-Rückgabe
        """
        # Exponentielles Strafmodell basierend auf k-Wert
        if delegation.k_value is None:
            return Decimal('0.0')
        
        # Strafe = e^(k_value * penalty_factor)
        penalty_factor = Decimal('0.5')
        
        try:
            penalty = (delegation.k_value * penalty_factor).exp()
        except (OverflowError, Decimal.Overflow):
            penalty = Decimal('100.0')  # Maximale Strafe
        
        return penalty
    
    def calculate_k_median(self, entity_id: str) -> Decimal:
        """
        Berechnet k-Median für Entity
        """
        if entity_id not in self.k_history or not self.k_history[entity_id]:
            return Decimal('0.0')
        
        k_values = sorted(self.k_history[entity_id])
        n = len(k_values)
        
        if n % 2 == 1:
            return k_values[n // 2]
        else:
            return (k_values[n // 2 - 1] + k_values[n // 2]) / Decimal('2.0')
    
    def evaluate_k_penalty(self, entity_id: str, current_k: Decimal) -> Decimal:
        """
        Berechnet k-basierte Strafe für überhöhte Komplexität
        """
        k_median = self.calculate_k_median(entity_id)
        
        if k_median == 0 or current_k <= k_median:
            return Decimal('0.0')
        
        # Exponentielles Strafmodell
        penalty_factor = Decimal('0.8')
        k_ratio = current_k / k_median
        
        try:
            penalty = (penalty_factor * k_ratio).exp()
        except (OverflowError, Decimal.Overflow):
            penalty = Decimal('50.0')  # Maximale k-Strafe
        
        return penalty
    
    def get_delegation_statistics(self, entity_id: str) -> Dict:
        """
        Statistiken für eine Entity
        """
        delegations_as_delegator = [
            d for d in self.delegations.values() 
            if d.delegator.entity_id == entity_id
        ]
        
        delegations_as_delegate = [
            d for d in self.delegations.values() 
            if d.delegate.entity_id == entity_id
        ]
        
        completed_delegations = [
            d for d in delegations_as_delegator 
            if d.status == DelegationStatus.COMPLETED
        ]
        
        returned_delegations = [
            d for d in delegations_as_delegator 
            if d.status == DelegationStatus.RETURNED
        ]
        
        return {
            "delegations_given": len(delegations_as_delegator),
            "delegations_received": len(delegations_as_delegate),
            "completed_delegations": len(completed_delegations),
            "returned_delegations": len(returned_delegations),
            "return_ratio": (len(returned_delegations) / max(len(delegations_as_delegator), 1)),
            "k_median": str(self.calculate_k_median(entity_id)),
            "k_history_length": len(self.k_history.get(entity_id, []))
        }

# Demonstration
def demonstrate_delegation_system():
    """Demonstration des theoretisch konsistenten Delegation-Systems"""
    
    from xinf_core_v3 import SystemState, CapPotentialProcessor
    
    # System initialisieren
    system_state = SystemState()
    cap_processor = CapPotentialProcessor(system_state)
    delegation_processor = DelegationProcessor(cap_processor)
    
    # Entities erstellen
    entity_strong = Entity("Strong", cap_base=Decimal('1.0'), cap_bge=Decimal('1.0'))
    entity_weak = Entity("Weak", cap_base=Decimal('1.0'), cap_bge=Decimal('0.2'))
    
    # Einige Cap_Past-Werte simulieren
    entity_strong.cap_past_components["test_domain"] = Decimal('2.0')
    entity_weak.cap_past_components["test_domain"] = Decimal('0.1')
    
    domain = "test_domain"
    
    print("=== Delegation System Demonstration ===")
    print(f"Strong Cap_Potential: {entity_strong.get_cap_potential(domain)}")
    print(f"Weak Cap_Potential: {entity_weak.get_cap_potential(domain)}")
    
    # Delegation initiieren
    delegation_id = delegation_processor.initiate_delegation(
        entity_strong, entity_weak, "task_1", domain, 
        "Complex analysis task", Decimal('2.0')
    )
    
    if delegation_id:
        print(f"Delegation created: {delegation_id}")
        
        delegation = delegation_processor.delegations[delegation_id]
        print(f"k-Value: {delegation.k_value}")
        
        # Feedback simulieren
        feedback_entries = [
            (entity_strong, "delegator_feedback", Decimal('0.7')),
            (entity_weak, "self_evaluation", Decimal('0.6'))
        ]
        
        # Delegation abschließen
        success = delegation_processor.complete_delegation(delegation_id, feedback_entries)
        print(f"Delegation completed: {success}")
        
        if success:
            print(f"Delegate effect: {delegation.delegate_effect}")
            print(f"Delegator effect: {delegation.delegator_effect}")
            
            # Aktualisierte Cap-Werte
            print(f"Updated Strong Cap_Potential: {entity_strong.get_cap_potential(domain)}")
            print(f"Updated Weak Cap_Potential: {entity_weak.get_cap_potential(domain)}")
        
        # Statistiken
        stats = delegation_processor.get_delegation_statistics("Strong")
        print(f"Strong delegation stats: {stats}")
    
    else:
        print("Delegation failed - insufficient capacity")

if __name__ == "__main__":
    demonstrate_delegation_system()
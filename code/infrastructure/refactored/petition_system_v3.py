# petition_system_v3.py - Theoretisch konsistentes Petition-System
# Basiert auf korrekten Formeln aus "Physics of Symbiotic Being"

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, getcontext
from enum import Enum
import uuid

from xinf_core_v3 import Entity, FeedbackWeighting, PetitionPriority

# Präzise Berechnungen
getcontext().prec = 28

class PetitionStatus(Enum):
    """Status einer Petition"""
    OPEN = "open"
    FULFILLED = "fulfilled"
    CLOSED = "closed"
    DELEGATED = "delegated"

class PetitionType(Enum):
    """Typ der Petition"""
    NEED = "need"           # Zielbedürfnis ("Wozu?")
    CAPABILITY = "capability"  # Fähigkeitsangebot ("Wie?")

@dataclass
class Petition:
    """Theoretisch konsistente Petition-Struktur"""
    petition_id: str
    petitioner: Entity
    domain: str
    description: str
    petition_type: PetitionType
    supporters: Set[str] = field(default_factory=set)  # Entity-IDs
    status: PetitionStatus = PetitionStatus.OPEN
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Theoretische Werte
    initial_priority: Optional[Decimal] = None
    current_score: Optional[Decimal] = None
    feedback_entries: List[Tuple[str, Decimal]] = field(default_factory=list)  # (entity_id, score)
    
    def __post_init__(self):
        """Berechnet initiale Priorität bei Erstellung"""
        if self.initial_priority is None:
            self.initial_priority = PetitionPriority.calculate_initial_priority(
                self.petitioner, self.domain
            )

class PetitionBroker:
    """Intelligenter Petition-Broker für Clustering und Zuweisung"""
    
    def __init__(self):
        self.petitions: Dict[str, Petition] = {}
        self.entity_registry: Dict[str, Entity] = {}
        self.domain_clusters: Dict[str, List[str]] = {}  # domain -> petition_ids
    
    def register_entity(self, entity: Entity):
        """Registriert eine Entity im System"""
        self.entity_registry[entity.entity_id] = entity
    
    def submit_petition(self, petitioner_id: str, domain: str, 
                       description: str, petition_type: PetitionType) -> str:
        """
        Erstellt neue Petition mit theoretisch korrekter Prioritätsberechnung
        """
        if petitioner_id not in self.entity_registry:
            raise ValueError(f"Petitioner {petitioner_id} not registered")
        
        petitioner = self.entity_registry[petitioner_id]
        petition_id = f"PET-{uuid.uuid4().hex[:8]}"
        
        petition = Petition(
            petition_id=petition_id,
            petitioner=petitioner,
            domain=domain,
            description=description,
            petition_type=petition_type
        )
        
        # Petitioner als ersten Unterstützer hinzufügen
        petition.supporters.add(petitioner_id)
        
        # Petition registrieren
        self.petitions[petition_id] = petition
        
        # Domain-Clustering
        if domain not in self.domain_clusters:
            self.domain_clusters[domain] = []
        self.domain_clusters[domain].append(petition_id)
        
        return petition_id
    
    def support_petition(self, petition_id: str, supporter_id: str) -> bool:
        """
        Unterstützt eine Petition (theoretisch korrekt)
        """
        if petition_id not in self.petitions:
            return False
        
        if supporter_id not in self.entity_registry:
            return False
        
        petition = self.petitions[petition_id]
        
        if petition.status != PetitionStatus.OPEN:
            return False
        
        # Berechtigung prüfen (Cap_Potential > 0 in Domain)
        supporter = self.entity_registry[supporter_id]
        cap_potential = supporter.get_cap_potential(petition.domain)
        
        if cap_potential <= 0:
            return False
        
        petition.supporters.add(supporter_id)
        
        # Score neu berechnen
        petition.current_score = self._calculate_petition_score(petition)
        
        return True
    
    def _calculate_petition_score(self, petition: Petition) -> Decimal:
        """
        Theoretisch korrekte Score-Berechnung:
        Score = Σ(w_{E'}) für alle Unterstützer
        """
        total_score = Decimal('0.0')
        
        for supporter_id in petition.supporters:
            if supporter_id in self.entity_registry:
                supporter = self.entity_registry[supporter_id]
                w_e = FeedbackWeighting.calculate_w_e(supporter, petition.domain)
                total_score += w_e
        
        return total_score
    
    def get_prioritized_petitions(self, domain: str, 
                                 threshold: Decimal = Decimal('1.0')) -> List[Petition]:
        """
        Liefert priorisierte Petitions in einer Domain
        """
        if domain not in self.domain_clusters:
            return []
        
        domain_petitions = []
        for petition_id in self.domain_clusters[domain]:
            petition = self.petitions[petition_id]
            
            if petition.status == PetitionStatus.OPEN:
                if petition.current_score is None:
                    petition.current_score = self._calculate_petition_score(petition)
                
                if petition.current_score >= threshold:
                    domain_petitions.append(petition)
        
        # Sortiert nach Score (absteigend)
        return sorted(domain_petitions, key=lambda p: p.current_score, reverse=True)
    
    def cluster_similar_petitions(self, domain: str) -> List[List[str]]:
        """
        Clustert ähnliche Petitions für effiziente Bearbeitung
        """
        if domain not in self.domain_clusters:
            return []
        
        petition_ids = self.domain_clusters[domain]
        
        # Vereinfachtes Clustering (in Realität: NLP-basiert)
        need_petitions = []
        capability_petitions = []
        
        for petition_id in petition_ids:
            petition = self.petitions[petition_id]
            if petition.petition_type == PetitionType.NEED:
                need_petitions.append(petition_id)
            else:
                capability_petitions.append(petition_id)
        
        clusters = []
        if need_petitions:
            clusters.append(need_petitions)
        if capability_petitions:
            clusters.append(capability_petitions)
        
        return clusters
    
    def match_needs_with_capabilities(self, domain: str) -> List[Tuple[str, str]]:
        """
        Matching zwischen Bedürfnissen und Fähigkeiten
        """
        clusters = self.cluster_similar_petitions(domain)
        matches = []
        
        if len(clusters) >= 2:
            need_cluster = clusters[0]
            capability_cluster = clusters[1]
            
            # Vereinfachtes Matching (in Realität: semantische Analyse)
            for need_id in need_cluster:
                for capability_id in capability_cluster:
                    need_petition = self.petitions[need_id]
                    capability_petition = self.petitions[capability_id]
                    
                    # Matching-Score basierend auf Prioritäten
                    if (need_petition.initial_priority and 
                        capability_petition.initial_priority and
                        abs(need_petition.initial_priority - capability_petition.initial_priority) < Decimal('0.5')):
                        matches.append((need_id, capability_id))
        
        return matches

class PetitionFeedbackSystem:
    """Feedback-System für abgeschlossene Petitions"""
    
    def __init__(self, broker: PetitionBroker):
        self.broker = broker
        self.feedback_database: Dict[str, List[Tuple[str, Decimal, datetime]]] = {}
    
    def submit_feedback(self, petition_id: str, evaluator_id: str, 
                       score: Decimal) -> bool:
        """
        Feedback zu erfüllter Petition (theoretisch korrekt gewichtet)
        """
        if petition_id not in self.broker.petitions:
            return False
        
        if evaluator_id not in self.broker.entity_registry:
            return False
        
        petition = self.broker.petitions[petition_id]
        
        # Nur erfüllte Petitions können bewertet werden
        if petition.status != PetitionStatus.FULFILLED:
            return False
        
        # Feedback mit Zeitstempel speichern
        if petition_id not in self.feedback_database:
            self.feedback_database[petition_id] = []
        
        self.feedback_database[petition_id].append(
            (evaluator_id, score, datetime.utcnow())
        )
        
        return True
    
    def calculate_weighted_petition_effect(self, petition_id: str) -> Decimal:
        """
        Berechnet gewichteten Effekt einer Petition basierend auf Feedback
        """
        if petition_id not in self.feedback_database:
            return Decimal('0.0')
        
        petition = self.broker.petitions[petition_id]
        feedback_entries = self.feedback_database[petition_id]
        
        weighted_sum = Decimal('0.0')
        for evaluator_id, score, _ in feedback_entries:
            if evaluator_id in self.broker.entity_registry:
                evaluator = self.broker.entity_registry[evaluator_id]
                w_e = FeedbackWeighting.calculate_w_e(evaluator, petition.domain)
                weighted_sum += score * w_e
        
        return weighted_sum
    
    def enforce_petitioner_feedback_requirement(self, petition_id: str) -> bool:
        """
        Stellt sicher, dass Petitioner Feedback abgegeben hat
        """
        petition = self.broker.petitions[petition_id]
        
        if petition.status != PetitionStatus.FULFILLED:
            return True  # Noch nicht erforderlich
        
        if petition_id not in self.feedback_database:
            return False  # Kein Feedback vorhanden
        
        feedback_entries = self.feedback_database[petition_id]
        petitioner_feedback = any(
            evaluator_id == petition.petitioner.entity_id 
            for evaluator_id, _, _ in feedback_entries
        )
        
        return petitioner_feedback

# Demonstration des refactored Systems
def demonstrate_petition_system():
    """Demonstration des theoretisch konsistenten Petition-Systems"""
    
    # System initialisieren
    broker = PetitionBroker()
    feedback_system = PetitionFeedbackSystem(broker)
    
    # Entities erstellen
    entity_a = Entity("A", cap_base=Decimal('1.0'), cap_bge=Decimal('0.5'))
    entity_b = Entity("B", cap_base=Decimal('1.0'), cap_bge=Decimal('0.2'))
    entity_c = Entity("C", cap_base=Decimal('1.0'), cap_bge=Decimal('0.8'))
    
    # Entities registrieren
    for entity in [entity_a, entity_b, entity_c]:
        broker.register_entity(entity)
    
    domain = "test_domain"
    
    print("=== Petition System Demonstration ===")
    
    # Petition erstellen
    petition_id = broker.submit_petition(
        "A", domain, "Need better documentation system", PetitionType.NEED
    )
    print(f"Created petition: {petition_id}")
    
    # Petition unterstützen
    support_b = broker.support_petition(petition_id, "B")
    support_c = broker.support_petition(petition_id, "C")
    print(f"Support from B: {support_b}, Support from C: {support_c}")
    
    # Petition-Details anzeigen
    petition = broker.petitions[petition_id]
    print(f"Initial Priority: {petition.initial_priority}")
    print(f"Current Score: {petition.current_score}")
    print(f"Supporters: {petition.supporters}")
    
    # Priorisierte Petitions abrufen
    prioritized = broker.get_prioritized_petitions(domain, Decimal('1.0'))
    print(f"Prioritized petitions: {len(prioritized)}")
    
    # Petition als erfüllt markieren
    petition.status = PetitionStatus.FULFILLED
    
    # Feedback abgeben
    feedback_system.submit_feedback(petition_id, "A", Decimal('0.8'))
    feedback_system.submit_feedback(petition_id, "B", Decimal('0.6'))
    
    # Gewichteten Effekt berechnen
    effect = feedback_system.calculate_weighted_petition_effect(petition_id)
    print(f"Weighted petition effect: {effect}")
    
    # Petitioner-Feedback prüfen
    has_petitioner_feedback = feedback_system.enforce_petitioner_feedback_requirement(petition_id)
    print(f"Petitioner provided feedback: {has_petitioner_feedback}")

if __name__ == "__main__":
    demonstrate_petition_system()
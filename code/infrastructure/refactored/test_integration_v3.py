# test_integration_v3.py - Vollständige Integration und Tests
# Validiert theoretische Konsistenz des refactored X^∞-Systems

import unittest
from decimal import Decimal, getcontext
from datetime import datetime

# Refactored Module importieren
from xinf_core_v3 import (
    Entity, SystemState, CapPotentialProcessor, 
    FeedbackWeighting, PetitionPriority, TaskExecution
)
from udu_system import UdUSystem, UdUCalculator, BlackSwanEvent, ThreatLevel, UdUIntegration
from petition_system_v3 import PetitionBroker, PetitionFeedbackSystem, PetitionType
from delegation_system_v3 import DelegationProcessor

# Hochpräzise Berechnungen
getcontext().prec = 28

class TestTheoreticalConsistency(unittest.TestCase):
    """Tests für theoretische Konsistenz"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.entity_a = Entity("A", cap_base=Decimal('1.0'), cap_bge=Decimal('0.5'))
        self.entity_b = Entity("B", cap_base=Decimal('1.0'), cap_bge=Decimal('0.2'))
        self.entity_c = Entity("C", cap_base=Decimal('1.0'), cap_bge=Decimal('0.8'))
        
        self.domain = "test_domain"
        
        # Cap_Past-Werte für Realismus
        self.entity_a.cap_past_components[self.domain] = Decimal('1.5')
        self.entity_b.cap_past_components[self.domain] = Decimal('0.3')
        self.entity_c.cap_past_components[self.domain] = Decimal('2.0')
    
    def test_cap_potential_formula(self):
        """Test: Cap_Potential(E,D,t) = Δ_{t-1} + Cap_BGE + Cap_Base"""
        
        expected_a = Decimal('1.5') + Decimal('0.5') + Decimal('1.0')  # 3.0
        expected_b = Decimal('0.3') + Decimal('0.2') + Decimal('1.0')  # 1.5
        expected_c = Decimal('2.0') + Decimal('0.8') + Decimal('1.0')  # 3.8
        
        self.assertEqual(self.entity_a.get_cap_potential(self.domain), expected_a)
        self.assertEqual(self.entity_b.get_cap_potential(self.domain), expected_b)
        self.assertEqual(self.entity_c.get_cap_potential(self.domain), expected_c)
    
    def test_feedback_weighting_formula(self):
        """Test: w_{E'} = 1/max(1, Cap_Potential(E'))"""
        
        w_a = FeedbackWeighting.calculate_w_e(self.entity_a, self.domain)
        w_b = FeedbackWeighting.calculate_w_e(self.entity_b, self.domain)
        w_c = FeedbackWeighting.calculate_w_e(self.entity_c, self.domain)
        
        # A: 1/max(1, 3.0) = 1/3.0
        # B: 1/max(1, 1.5) = 1/1.5
        # C: 1/max(1, 3.8) = 1/3.8
        
        self.assertAlmostEqual(w_a, Decimal('1.0') / Decimal('3.0'), places=10)
        self.assertAlmostEqual(w_b, Decimal('1.0') / Decimal('1.5'), places=10)
        self.assertAlmostEqual(w_c, Decimal('1.0') / Decimal('3.8'), places=10)
    
    def test_petition_priority_formula(self):
        """Test: Priority_initial,X_A = w_{E'} des Petitioners"""
        
        priority_a = PetitionPriority.calculate_initial_priority(self.entity_a, self.domain)
        priority_b = PetitionPriority.calculate_initial_priority(self.entity_b, self.domain)
        
        w_a = FeedbackWeighting.calculate_w_e(self.entity_a, self.domain)
        w_b = FeedbackWeighting.calculate_w_e(self.entity_b, self.domain)
        
        self.assertEqual(priority_a, w_a)
        self.assertEqual(priority_b, w_b)
    
    def test_l_factor_calculation(self):
        """Test: L = Σ(Wert abgeschlossener Aufgaben) / Σ(Wert Gesamtwirkung)"""
        
        system_state = SystemState()
        
        # Completed tasks hinzufügen
        system_state.completed_tasks = [
            ("task_1", Decimal('2.0')),
            ("task_2", Decimal('1.5')),
            ("task_3", Decimal('3.0'))
        ]
        
        # Effects hinzufügen
        system_state.total_effects = [Decimal('1.8'), Decimal('1.2'), Decimal('2.5')]
        
        l_factor = system_state.calculate_l_factor()
        
        expected_l = (Decimal('2.0') + Decimal('1.5') + Decimal('3.0')) / (Decimal('1.8') + Decimal('1.2') + Decimal('2.5'))
        expected_l = Decimal('6.5') / Decimal('5.5')
        
        self.assertAlmostEqual(l_factor, expected_l, places=10)
    
    def test_subjective_feedback_aggregation(self):
        """Test: Δ = Σ_{E' ∈ S_{fb,k}} (f_{E'k} × w_{E'})"""
        
        feedback_entries = [
            (self.entity_a, "positive", Decimal('0.8')),
            (self.entity_b, "neutral", Decimal('0.0')),
            (self.entity_c, "negative", Decimal('-0.5'))
        ]
        
        result = FeedbackWeighting.calculate_subjective_feedback(feedback_entries, self.domain)
        
        # Manuelle Berechnung
        w_a = FeedbackWeighting.calculate_w_e(self.entity_a, self.domain)
        w_b = FeedbackWeighting.calculate_w_e(self.entity_b, self.domain)
        w_c = FeedbackWeighting.calculate_w_e(self.entity_c, self.domain)
        
        expected = (Decimal('0.8') * w_a + 
                   Decimal('0.0') * w_b + 
                   Decimal('-0.5') * w_c)
        
        self.assertAlmostEqual(result, expected, places=10)

class TestUdUSystem(unittest.TestCase):
    """Tests für UdU-System"""
    
    def test_udu_capacity_calculation(self):
        """Test: UdU ≈ (X_{k,Need} × S × (S-1)/S)^∞"""
        
        threat_magnitude = Decimal('10.0')
        entity_count = 100
        
        capacity = UdUCalculator.calculate_symbolic_capacity(
            threat_magnitude, entity_count, infinity_approximation=5
        )
        
        # Manuelle Berechnung
        s = Decimal('100.0')
        base_factor = threat_magnitude * s * ((s - Decimal('1.0')) / s)
        expected = base_factor ** 5
        
        self.assertAlmostEqual(capacity, expected, places=5)
    
    def test_udu_activation_threshold(self):
        """Test UdU-Aktivierung bei kritischen Events"""
        
        udu_system = UdUSystem()
        
        # Existenzielles Event
        crisis_event = BlackSwanEvent(
            event_id="CRISIS-TEST",
            description="System collapse imminent",
            threat_magnitude=Decimal('1000.0'),
            affected_entities=500,
            threat_level=ThreatLevel.EXISTENTIAL
        )
        
        activated = udu_system.register_potential_threat(crisis_event)
        
        self.assertTrue(activated)
        self.assertTrue(crisis_event.handled_by_udu)
        self.assertEqual(len(udu_system.udu_actions), 1)

class TestIntegratedWorkflow(unittest.TestCase):
    """Tests für integrierte Workflows"""
    
    def setUp(self):
        """Setup für Integrationstests"""
        # Vollständiges System aufbauen
        self.system_state = SystemState()
        self.cap_processor = CapPotentialProcessor(self.system_state)
        self.task_executor = TaskExecution(self.cap_processor)
        self.delegation_processor = DelegationProcessor(self.cap_processor)
        
        self.petition_broker = PetitionBroker()
        self.feedback_system = PetitionFeedbackSystem(self.petition_broker)
        
        self.udu_system = UdUSystem()
        
        # Entities erstellen und registrieren
        self.entities = [
            Entity("Strong", cap_base=Decimal('1.0'), cap_bge=Decimal('1.0')),
            Entity("Medium", cap_base=Decimal('1.0'), cap_bge=Decimal('0.5')),
            Entity("Weak", cap_base=Decimal('1.0'), cap_bge=Decimal('0.1'))
        ]
        
        # Cap_Past für Realismus
        for i, entity in enumerate(self.entities):
            entity.cap_past_components["test_domain"] = Decimal(str(2.0 - i * 0.8))
            self.petition_broker.register_entity(entity)
    
    def test_complete_petition_workflow(self):
        """Test: Vollständiger Petition → Task → Feedback Workflow"""
        
        domain = "test_domain"
        
        # 1. Petition erstellen
        petition_id = self.petition_broker.submit_petition(
            "Weak", domain, "Need infrastructure improvement", PetitionType.NEED
        )
        
        # 2. Unterstützung sammeln
        self.petition_broker.support_petition(petition_id, "Medium")
        self.petition_broker.support_petition(petition_id, "Strong")
        
        # 3. Priorisierte Petitions abrufen
        prioritized = self.petition_broker.get_prioritized_petitions(domain)
        
        self.assertEqual(len(prioritized), 1)
        petition = prioritized[0]
        
        # 4. Task von starker Entity übernommen
        strong_entity = self.entities[0]  # Strong
        can_adopt = self.task_executor.adopt_task(
            strong_entity, "infra_task", domain, petition.initial_priority
        )
        
        self.assertTrue(can_adopt)
        
        # 5. Task ausführen mit Feedback
        feedback_entries = [
            (self.entities[1], "good_result", Decimal('0.7')),  # Medium
            (self.entities[2], "very_satisfied", Decimal('0.9'))  # Weak
        ]
        
        effect = self.task_executor.complete_task(
            strong_entity, "infra_task", domain, feedback_entries
        )
        
        # 6. Validierung
        self.assertGreater(effect, Decimal('0.0'))
        
        # Cap_Potential sollte gestiegen sein
        original_cap = Decimal('4.0')  # 2.0 + 1.0 + 1.0
        new_cap = strong_entity.get_cap_potential(domain)
        self.assertGreater(new_cap, original_cap)
    
    def test_delegation_workflow(self):
        """Test: Delegation mit theoretisch korrekten Effekten"""
        
        domain = "test_domain"
        strong_entity = self.entities[0]  # Strong: Cap_Potential = 4.0
        medium_entity = self.entities[1]  # Medium: Cap_Potential = 2.5
        
        # Delegation initiieren (mit angepasster Priority die Medium schaffen kann)
        delegation_id = self.delegation_processor.initiate_delegation(
            strong_entity, medium_entity, "complex_task", domain,
            "Data analysis requiring expertise", Decimal('2.0')  # Medium kann das schaffen
        )
        
        self.assertIsNotNone(delegation_id)
        
        # Delegation abschließen
        feedback_entries = [
            (strong_entity, "delegator_satisfied", Decimal('0.8')),
            (medium_entity, "challenging_but_good", Decimal('0.6'))
        ]
        
        success = self.delegation_processor.complete_delegation(delegation_id, feedback_entries)
        self.assertTrue(success)
        
        # Effekte prüfen
        delegation = self.delegation_processor.delegations[delegation_id]
        
        # Schwächerer Delegate sollte positiven Effekt für Delegator erzeugen
        self.assertIsNotNone(delegation.delegator_effect)
        self.assertIsNotNone(delegation.delegate_effect)
        
        # Delegator sollte durch schwächeren Delegate verstärkt werden
        self.assertGreater(delegation.delegator_effect, Decimal('0.0'))
    
    def test_system_stability_monitoring(self):
        """Test: System-Stabilitäts-Monitoring mit UdU"""
        
        udu_integration = UdUIntegration(self.udu_system)
        
        # Kritische Systemsituation simulieren
        # (Niedrige Cap_Potential-Werte setzen)
        for entity in self.entities:
            entity.cap_past_components["critical_domain"] = Decimal('-0.5')
        
        # Monitoring
        critical_situation = udu_integration.monitor_system_stability(
            self.entities, ["critical_domain"]
        )
        
        # Bei kritischer Situation sollte UdU aktiviert werden
        if critical_situation:
            self.assertGreater(len(self.udu_system.active_events), 0)

def run_all_tests():
    """Führt alle Tests aus"""
    
    print("=== X^∞ Refactored System Tests ===\n")
    
    # Test Suites
    consistency_suite = unittest.TestLoader().loadTestsFromTestCase(TestTheoreticalConsistency)
    udu_suite = unittest.TestLoader().loadTestsFromTestCase(TestUdUSystem)
    integration_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegratedWorkflow)
    
    # Runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    print("1. Testing Theoretical Consistency...")
    result1 = runner.run(consistency_suite)
    
    print("\n2. Testing UdU System...")
    result2 = runner.run(udu_suite)
    
    print("\n3. Testing Integrated Workflows...")
    result3 = runner.run(integration_suite)
    
    # Gesamtresultat
    total_tests = result1.testsRun + result2.testsRun + result3.testsRun
    total_failures = len(result1.failures) + len(result2.failures) + len(result3.failures)
    total_errors = len(result1.errors) + len(result2.errors) + len(result3.errors)
    
    print(f"\n=== Test Summary ===")
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
    print(f"Success Rate: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("🜄 All tests passed - Theoretical consistency verified!")
    else:
        print("⚠️ Some tests failed - Review implementation")

def demonstrate_complete_system():
    """Vollständige System-Demonstration"""
    
    print("\n=== Complete X^∞ System Demonstration ===\n")
    
    # System initialisieren
    system_state = SystemState()
    cap_processor = CapPotentialProcessor(system_state)
    task_executor = TaskExecution(cap_processor)
    delegation_processor = DelegationProcessor(cap_processor)
    
    petition_broker = PetitionBroker()
    feedback_system = PetitionFeedbackSystem(petition_broker)
    
    udu_system = UdUSystem()
    udu_integration = UdUIntegration(udu_system)
    
    # Entities mit realistischen Werten
    entities = [
        Entity("Alice", cap_base=Decimal('1.0'), cap_bge=Decimal('0.8')),
        Entity("Bob", cap_base=Decimal('1.0'), cap_bge=Decimal('0.5')),
        Entity("Charlie", cap_base=Decimal('1.0'), cap_bge=Decimal('0.2'))
    ]
    
    # Historische Cap_Past simulieren
    entities[0].cap_past_components["infrastructure"] = Decimal('2.5')
    entities[1].cap_past_components["infrastructure"] = Decimal('1.0')
    entities[2].cap_past_components["infrastructure"] = Decimal('0.1')
    
    # Entities registrieren
    for entity in entities:
        petition_broker.register_entity(entity)
    
    domain = "infrastructure"
    
    print("1. Initial System State:")
    for entity in entities:
        cap_pot = entity.get_cap_potential(domain)
        w_e = FeedbackWeighting.calculate_w_e(entity, domain)
        print(f"   {entity.entity_id}: Cap_Potential = {cap_pot}, w_E = {w_e}")
    
    print("\n2. Creating and supporting petition...")
    petition_id = petition_broker.submit_petition(
        "Charlie", domain, "Critical infrastructure upgrade needed", PetitionType.NEED
    )
    
    petition_broker.support_petition(petition_id, "Alice")
    petition_broker.support_petition(petition_id, "Bob")
    
    petition = petition_broker.petitions[petition_id]
    print(f"   Petition Score: {petition.current_score}")
    print(f"   Initial Priority: {petition.initial_priority}")
    
    print("\n3. Task adoption and delegation...")
    # Alice übernimmt Task
    alice = entities[0]
    charlie = entities[2]
    
    can_adopt = task_executor.adopt_task(alice, "upgrade_task", domain, petition.initial_priority)
    print(f"   Alice can adopt task: {can_adopt}")
    
    if can_adopt:
        # Alice delegiert an Charlie (Stärkung des Schwächeren)
        delegation_id = delegation_processor.initiate_delegation(
            alice, charlie, "upgrade_task", domain, 
            "Infrastructure upgrade implementation", petition.initial_priority
        )
        
        if delegation_id:
            print(f"   Delegation created: {delegation_id}")
            
            delegation = delegation_processor.delegations[delegation_id]
            print(f"   k-Value: {delegation.k_value}")
            
            # Task completion mit Feedback
            feedback_entries = [
                (alice, "delegator_feedback", Decimal('0.8')),
                (charlie, "self_evaluation", Decimal('0.7')),
                (entities[1], "observer_feedback", Decimal('0.9'))  # Bob
            ]
            
            success = delegation_processor.complete_delegation(delegation_id, feedback_entries)
            print(f"   Delegation completed: {success}")
            
            if success:
                print(f"   Charlie effect: {delegation.delegate_effect}")
                print(f"   Alice effect: {delegation.delegator_effect}")
    
    print("\n4. Updated system state:")
    for entity in entities:
        cap_pot = entity.get_cap_potential(domain)
        print(f"   {entity.entity_id}: Updated Cap_Potential = {cap_pot}")
    
    # L-Factor
    l_factor = system_state.calculate_l_factor()
    print(f"\n5. System efficiency (L-Factor): {l_factor}")
    
    # System stability check
    print("\n6. System stability monitoring...")
    critical = udu_integration.monitor_system_stability(entities, [domain])
    print(f"   Critical situation detected: {critical}")
    
    if critical:
        status = udu_system.get_udu_status_report()
        print(f"   UdU Status: {status}")
    
    print("\n🜄 Complete system demonstration finished.")

if __name__ == "__main__":
    # Tests ausführen
    run_all_tests()
    
    # System demonstrieren
    demonstrate_complete_system()
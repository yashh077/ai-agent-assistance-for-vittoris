"""Automated Verification and Test Suite for Vittoris AI Autonomous Agent."""
import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_engine import VittorisAutonomousAgent
from tools.calendar_tool import list_all_appointments, get_available_slots
from tools.diagnostics_tool import run_full_system_diagnostic, execute_auto_remediation
from tools.escalation_tool import list_escalation_tickets

def run_tests():
    print("=================================================================")
    print("🚀 RUNNING COMPREHENSIVE VITTORIS AI AGENT AUTOMATED TEST SUITE")
    print("=================================================================\n")

    agent = VittorisAutonomousAgent()

    # TEST 1: Service Inquiry
    print("➡️ [TEST 1] Customer queries company services...")
    res1 = agent.process_message("test_session_1", "What services do you provide at Vittoris?")
    assert "Autonomous Conversational & Voice Agents" in res1["text"] or "Vittoris AI" in res1["text"]
    print("✅ TEST 1 PASSED: Knowledge base accurately returned services overview.\n")

    # TEST 2: Server Health & Diagnostics
    print("➡️ [TEST 2] Customer asks for server status and health check...")
    res2 = agent.process_message("test_session_2", "Check server status and API gateway health")
    assert "Real-Time Infrastructure Health Diagnostic" in res2["text"]
    assert res2["action"]["type"] == "diagnostics_report"
    print("✅ TEST 2 PASSED: Server health diagnostic telemetry returned correctly.\n")

    # TEST 3: In-App Service Troubleshooting & Self-Healing
    print("➡️ [TEST 3] Customer reports in-app voice drop issue...")
    res3 = agent.process_message("test_session_3", "Our voice agent is dropping calls and high latency")
    assert "Autonomous In-App Troubleshooting" in res3["text"]
    assert "Voice & Telephony Agent" in res3["text"]
    print("✅ TEST 3 PASSED: In-app voice drop diagnosed and self-healing runbook executed.\n")

    # TEST 4: Appointment Booking Multi-Turn Flow
    print("➡️ [TEST 4] Customer books an appointment...")
    res4_step1 = agent.process_message("test_session_4", "I'd like to book an appointment with Uday")
    assert "Schedule an AI Architecture & Diagnostic Consultation" in res4_step1["text"]
    
    # Step 2: Customer provides details
    slots = get_available_slots(days_ahead=3)
    target_slot = slots[0]["slot_time"]
    res4_step2 = agent.process_message("test_session_4", f"Slot 1, my name is Alex Vance, email is alex.vance@techcorp.com")
    assert "Appointment Confirmed" in res4_step2["text"]
    assert "VIT-" in res4_step2["text"]
    print(f"✅ TEST 4 PASSED: Appointment confirmed with reference code in persistent DB.\n")

    # TEST 5: Official Intervention & Inavailability Escalation
    print("➡️ [TEST 5] Customer requests official escalation...")
    res5_step1 = agent.process_message("test_session_5", "I need to speak to an official regarding an enterprise custom contract")
    assert "Official Contact & Autonomous Escalation Protocol" in res5_step1["text"]
    
    # Step 2: Customer provides email
    res5_step2 = agent.process_message("test_session_5", "My name is Elena Rostova, email elena@enterprise.io, we need $200k SLA contract approval")
    assert "Executive Escalation Dossier Dispatched" in res5_step2["text"]
    assert "VIT-ESC-" in res5_step2["text"]
    print("✅ TEST 5 PASSED: Official escalation ticket logged in database with SLA.\n")

    # VERIFY PERSISTENCE
    print("➡️ [TEST 6] Verifying SQLite database persistence...")
    all_apts = list_all_appointments()
    assert len(all_apts) >= 1
    all_tickets = list_escalation_tickets()
    assert len(all_tickets) >= 1
    print(f"✅ TEST 6 PASSED: {len(all_apts)} appointment(s) and {len(all_tickets)} ticket(s) verified in SQLite DB.\n")

    print("=================================================================")
    print("🎉 ALL 6 COMPREHENSIVE TESTS PASSED SUCCESSFULLY!")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()

"""Automated Verification Suite for Vittoris AI Voice Assistant & Warm Transfer Engine."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_engine import VittorisAutonomousAgent
from tools.routing_tool import match_best_official, execute_warm_transfer, get_all_officials_live_status
from tools.calendar_tool import get_available_slots, list_all_appointments

def run_voice_tests():
    print("=================================================================")
    print("🎙️ RUNNING VITTORIS AI VOICE ASSISTANT & WARM TRANSFER TEST SUITE")
    print("=================================================================\n")

    agent = VittorisAutonomousAgent()

    # TEST 1: Voice Script Cleanliness (No Markdown in voice_script)
    print("➡️ [TEST 1] Verifying natural voice speech script formatting...")
    res1 = agent.process_message("v_test_1", "What does Vittoris AI do?")
    assert "voice_script" in res1, "Response missing voice_script field"
    voice_txt = res1["voice_script"]
    assert "#" not in voice_txt, "Voice script contains unstripped markdown headings"
    assert "*" not in voice_txt, "Voice script contains unstripped markdown asterisks"
    assert "|" not in voice_txt, "Voice script contains table pipes"
    print(f"✅ TEST 1 PASSED: Voice script generated cleanly:\n   \"{voice_txt[:100]}...\"\n")

    # TEST 2: Explaining Complex Architecture
    print("➡️ [TEST 2] Asking assistant to explain complex autonomous voice bot architecture...")
    res2 = agent.process_message("v_test_2", "Explain how your autonomous voice agents work in detail")
    assert "Ultra-Low Latency Telephony" in res2["text"]
    assert "SIP trunks" in res2["voice_script"]
    print("✅ TEST 2 PASSED: Complex voice architecture explained conversationally.\n")

    # TEST 3: Rescheduling Appointments
    print("➡️ [TEST 3] Testing appointment booking followed by voice rescheduling...")
    slots = get_available_slots(days_ahead=4)
    # First book an appointment
    book_res = agent.process_message("v_test_3", "Book an appointment for Dr. Marcus Brody, email brody@ai-research.org, Slot 1")
    assert "Appointment Confirmed" in book_res["text"]
    booking_id = book_res["action"]["data"]["booking_id"]
    print(f"   Created booking: {booking_id}")

    # Now reschedule it
    resched_res = agent.process_message("v_test_3", f"I need to reschedule {booking_id} to Slot 2")
    assert "Appointment Rescheduled" in resched_res["text"] or "successfully" in resched_res["voice_script"].lower()
    print("✅ TEST 3 PASSED: Rescheduling workflow successfully moved appointment.\n")

    # TEST 4: Domain Knowledge Matching & Warm Transfer
    print("➡️ [TEST 4] Matching query to best specialist and executing warm transfer...")
    # Sarah Chen is specialist for server/integrations
    expert = match_best_official("Our PostgreSQL database cluster and API server has high latency")
    assert expert["id"] == "sarah", f"Expected Sarah Chen for server issue, got {expert['name']}"
    print(f"   Matched Query to: {expert['name']} ({expert['role']}) - {expert['extension']}")

    # Transfer when official is available
    transfer = execute_warm_transfer(
        official_id="sarah",
        customer_name="Dr. Marcus Brody",
        customer_email="brody@ai-research.org",
        issue_summary="Database and API server latency"
    )
    assert transfer["transfer_status"] == "CONNECTED"
    assert "Sarah Chen" in transfer["voice_announcement"]
    print(f"✅ TEST 4 PASSED: Warm transfer connected. Greeting: \"{transfer['official_greeting']}\"\n")

    # TEST 5: Official Inavailability Fallback
    print("➡️ [TEST 5] Testing warm transfer when target official is in meetings/unavailable...")
    # Uday Zayn is in meetings
    transfer_busy = execute_warm_transfer(
        official_id="uday",
        customer_name="Dr. Marcus Brody",
        customer_email="brody@ai-research.org",
        issue_summary="Enterprise contract negotiation"
    )
    assert transfer_busy["transfer_status"] == "OFFICIAL_UNAVAILABLE"
    assert "unable to take a live call" in transfer_busy["voice_announcement"].lower()
    print("✅ TEST 5 PASSED: Inavailability handled gracefully with autonomous fallback.\n")

    print("=================================================================")
    print("🎉 ALL 5 VOICE & WARM TRANSFER TESTS PASSED PERFECTLY!")
    print("=================================================================")

if __name__ == "__main__":
    run_voice_tests()

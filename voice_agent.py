"""Interactive Voice Assistant & Telephony Call Simulator for Vittoris AI."""
import sys
import time
import uuid
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_engine import VittorisAutonomousAgent
from tools.routing_tool import get_all_officials_live_status

# Try importing pyttsx3 safely
TTS_ENGINE = None
try:
    import pyttsx3
    TTS_ENGINE = pyttsx3.init()
    TTS_ENGINE.setProperty('rate', 175)
except Exception:
    TTS_ENGINE = None


def speak(text: str):
    """Speaks text using system TTS if available, else prints simulated spoken audio banner."""
    print(f"\n🔊 [Voice Audio Out] > \"{text}\"")
    if TTS_ENGINE:
        try:
            TTS_ENGINE.say(text)
            TTS_ENGINE.runAndWait()
        except Exception:
            pass


def main():
    agent = VittorisAutonomousAgent()
    session_id = f"voice_call_{uuid.uuid4().hex[:6]}"
    
    print("\n" + "=" * 65)
    print("📞 VITTORIS AI - AUTONOMOUS VOICE ASSISTANT & CALL ROUTER")
    print("=" * 65)
    print("Voice Features Active:")
    print("  • Speech synthesis voice responses (natural spoken dialogue)")
    print("  • Explains complex services (Voice Bots, Doc Intelligence, Infra)")
    print("  • Reschedules & cancels appointments conversationally")
    print("  • Live Warm Transfer: Bridges line to available specialists")
    print("    - Uday Zayn (Strategy/Pricing/Contracts) [Ext 101]")
    print("    - Sarah Chen (Server/Integrations/Pipelines) [Ext 102]")
    print("    - Marcus Vance (Voice Bots/Telephony/Sync) [Ext 103]")
    print("=" * 65 + "\n")
    
    welcome_speech = (
        "Thank you for calling Vittoris AI. I am your autonomous voice operations assistant. "
        "I can answer questions about our AI infrastructure, book or reschedule consultations, "
        "run server diagnostics, or connect you directly with our specialists. How can I help you today?"
    )
    speak(welcome_speech)
    
    while True:
        try:
            user_input = input("\n🎙️ Caller > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "hangup", "quit", "bye", "end call"]:
                speak("Thank you for calling Vittoris AI. Have a wonderful day. Goodbye!")
                break
                
            response = agent.process_message(session_id, user_input)
            
            # Play speech output
            voice_script = response.get("voice_script") or response.get("text")
            speak(voice_script)
            
            # Check if warm transfer occurred
            action = response.get("action", {})
            if action.get("type") == "warm_transfer_connected":
                transfer = action["transfer"]
                official = transfer["official"]
                print("\n" + "—" * 60)
                print(f"🔀 [CALL BRIDGED] Connecting to {official['name']} ({official['extension']})...")
                print(f"📋 Hand-off Dossier forward: Issue summary sent to specialist console.")
                print(f"🎙️ {official['name']} > \"{transfer['official_greeting']}\"")
                print("—" * 60)
                
        except (KeyboardInterrupt, EOFError):
            print("\n[Call Ended]")
            break


if __name__ == "__main__":
    main()

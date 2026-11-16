"""Interactive Command-Line Interface (CLI) for Vittoris AI Autonomous Agent."""
import sys
import uuid
from agent_engine import VittorisAutonomousAgent

def main():
    agent = VittorisAutonomousAgent()
    session_id = f"cli_{uuid.uuid4().hex[:6]}"
    
    print("\n=================================================================")
    print("⚡ VITTORIS AI - AUTONOMOUS ENTERPRISE OPERATIONS AGENT")
    print("=================================================================")
    print("Available capabilities:")
    print("  1. Inquire about services (Voice Agents, Lead Gen, AI Infrastructure)")
    print("  2. Check server health & diagnostics ('Check server health')")
    print("  3. Troubleshoot in-app issues ('Voice agent dropping calls', 'PDF stuck')")
    print("  4. Book an appointment ('Book an appointment with Uday')")
    print("  5. Official intervention escalation ('Speak to officials')")
    print("Type 'exit' or 'quit' to leave.\n")
    
    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting agent session. Goodbye!")
                break
                
            response = agent.process_message(session_id, user_input)
            print(f"\nVittoris Agent >\n{response['text']}")
            
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

if __name__ == "__main__":
    main()

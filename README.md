# ⚡ Vittoris AI Autonomous Operations & Voice Telephony Agent

An enterprise-grade **AI Voice Assistant cum Autonomous Operations Agent** engineered for **[Vittoris AI](https://vittoris.com)**. 

This agent handles voice and chat customer inquiries, reschedules and books appointments directly into calendars, explains complicated technical architectures (voice bots, document intelligence, operational pipelines), executes server diagnostics and self-healing runbooks in the absence of officials, and **dynamically executes Warm Transfers to connect customers with the exact company official who has the specialized knowledge to solve their problem** when they are available.

---

## 🌐 Live Server & Instant Cloud Deployment

| Platform | Live Access | Description |
| :--- | :--- | :--- |
| **GitHub Codespaces** | [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/yashh077/ai-agent-assistance-for-vittoris) | **1-Click Live Python Server on GitHub**: Boots up a cloud container on GitHub, installs dependencies, and runs `python app.py` with public live HTTPS preview! |
| **GitHub Pages** | [https://yashh077.github.io/ai-agent-assistance-for-vittoris/](https://yashh077.github.io/ai-agent-assistance-for-vittoris/) | **Instant 24/7 Live Web App**: Served directly by GitHub Pages with full Web Speech voice synthesis, mic input, and warm transfer simulations. |
| **Render Cloud** | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com) | Free production web service auto-deployed via `render.yaml`. |

---

## 🏗️ Architecture & Warm Transfer Routing

```
                             [Inbound Voice / Chat Customer]
                              (Browser WebRTC/Mic, SIP, Chat)
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │    Autonomous Voice Agent    │
                             │ (Speech-to-Text & Synthesizer)
                             └──────────────┬───────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────┐
                             │    Domain Knowledge Router   │
                             └───────┬──────────────┬───────┘
                                     │              │
                   ┌─────────────────┴────┐         └─────────────────┐
                   ▼                      ▼                           ▼
          [Official AVAILABLE]   [Official UNAVAILABLE]    [Self-Healing & Scheduling]
                   │                      │                           │
          ┌────────┴────────┐    ┌────────┴─────────┐        ┌────────┴─────────┐
          │  Warm Call      │    │ Autonomous       │        │ - Auto-Reschedule│
          │  Transfer       │    │ Fallback Voice   │        │ - Purge Cache    │
          │  - Uday (Ext 101)    │ - Explain Issue  │        │ - Restart Stream │
          │  - Sarah (Ext 102)   │ - Lock Calendar  │        │ - Vector Reindex │
          │  - Marcus (Ext 103)  │ - Emergency Alert│        │ - Issue Fixes    │
          └─────────────────┘    └──────────────────┘        └──────────────────┘
```

---

## 🌟 Key Capabilities

### 1. 🎙️ Natural Voice Conversations & Plain-English Explanations
* **Dual-Format Generation:** Every response generates both clean visual markdown (for screens) and a fluid, natural `voice_script` stripped of markdown symbols and formatted for speech synthesis.
* **Explaining Complicated Stuff:** Conversational, easy-to-understand voice breakdowns for complex architectures:
  * **Autonomous Voice Bots:** Explains the 3-layer architecture (sub-200ms SIP streaming, conversational LLM turn-taking, and live calendar API tool calls).
  * **Document Intelligence:** Explains optical character recognition, tabular invoice extraction, and dead-letter queue verification.
  * **Pay-per-Appointment Lead Funnels:** Explains how conversational funnels replace cold-outreach friction.

### 2. 📞 Dynamic Specialist Routing & Warm Call Transfers
When a customer needs help, the agent analyzes the domain of the problem and matches them to the official with the highest specialization:
* **Uday Zayn** (`Ext 101` - Founder & Lead AI Architect): Enterprise AI strategy, bespoke infrastructure, pricing, custom contract negotiations, and audits.
* **Sarah Chen** (`Ext 102` - Head of Enterprise Integrations): Server outages, API gateway issues, database & vector clusters, and PDF document pipelines.
* **Marcus Vance** (`Ext 103` - Senior Solutions Engineer): Telephony/SIP streams, audio latency/call drops, WhatsApp business chatbots, and calendar sync.

**The Warm Transfer Protocol:**
* **If the official is online & available:** The agent bridges the line, notifies the customer (*"I am bridging your line to Sarah Chen at Extension 102 who specializes in this exact pipeline..."*), forwards a diagnostic dossier, and simulates the official taking over the call with a personalized greeting!
* **If the official is in meetings or out of office:** The agent politely explains why the official is unavailable and either resolves the issue autonomously or books a priority 1-on-1 slot on their calendar.

### 3. 📅 Conversational Booking & Rescheduling
* **Voice Rescheduling:** Simply say *"I need to reschedule my appointment to a different slot"* or *"Move my booking VIT-F1B45C to Slot 2"*. The agent looks up existing bookings in SQLite, updates the timestamp, and confirms via voice.
* **Conflict Prevention:** Detects double-booking and offers alternative slots.

### 4. ⚡ In-App & Server Diagnostics with Self-Healing Runbooks
* **Telemetry Monitors:** Real-time health metrics across the API Gateway, Voice Stream Worker, Document Intelligence Pipeline, and Database Cluster.
* **Self-Healing Runbooks:** The agent autonomously executes fixes (e.g. `restart_voice_stream`, `purge_cache_and_recycle_pool`, `refresh_calendar_tokens`) so callers don't have to wait for an engineer.

---

## 📁 Project Structure

```
vittoris-ai-agent/
├── config.py             # Business hours, officials directory, services config
├── knowledge_base.py     # Vittoris AI services, technical case studies, and FAQs
├── agent_engine.py       # Core autonomous agent, voice script generator & router
├── voice_agent.py        # Dedicated interactive Voice Assistant CLI runner
├── app.py                # Flask Web application and REST API endpoints
├── cli.py                # Command-line text interface
├── test_agent.py         # Automated core operations test suite (6 tests)
├── test_voice_agent.py   # Automated voice & warm transfer test suite (5 tests)
├── tools/
│   ├── routing_tool.py     # Domain matching, official roster & warm transfer engine
│   ├── calendar_tool.py    # Appointment scheduling, rescheduling & SQLite database
│   ├── diagnostics_tool.py # Server health checks & self-healing runbooks
│   └── escalation_tool.py  # Emergency official escalation ticket dispatcher
├── templates/
│   └── index.html        # Enterprise dashboard with Live Voice Call simulator
├── static/
│   ├── style.css         # Dark-mode styling, audio visualizer waves & specialist cards
│   └── app.js            # Frontend Web Speech API, TTS, and telemetry monitors
└── vittoris_data.db      # SQLite persistent storage
```

---

## 🚀 How to Run and Test

### 1. Launch the Interactive Voice Dashboard
```powershell
python C:\Users\yashw\.gemini\antigravity\scratch\vittoris-ai-agent\app.py
```
Open **`http://127.0.0.1:5000`** in your browser.
* Click **"📞 Start Voice Call"** to initiate a live voice session. The agent will speak out loud through your speakers!
* Click the **Microphone (🎙️)** button to speak directly to the agent using browser Speech-to-Text.
* Open the **"👥 Specialists & Transfer"** tab to see live official availability and trigger 1-click warm transfers.

### 2. Run the Dedicated Voice Assistant in Terminal
```powershell
python C:\Users\yashw\.gemini\antigravity\scratch\vittoris-ai-agent\voice_agent.py
```

### 3. Run Both Test Suites
```powershell
python C:\Users\yashw\.gemini\antigravity\scratch\vittoris-ai-agent\test_voice_agent.py
python C:\Users\yashw\.gemini\antigravity\scratch\vittoris-ai-agent\test_agent.py
```

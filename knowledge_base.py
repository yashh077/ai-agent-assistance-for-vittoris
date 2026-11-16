"""Comprehensive Knowledge Base for Vittoris AI Services and Solutions."""

VITTORIS_KNOWLEDGE = {
    "company_overview": (
        "Vittoris AI (https://vittoris.com) is an outcome-driven AI services and enterprise infrastructure "
        "firm. Rather than offering a standard canned SaaS product, Vittoris engineers bespoke AI infrastructure, "
        "autonomous conversational voice/chat agents, and performance-based client acquisition systems designed "
        "to eliminate operational friction and human labor waste for modern businesses."
    ),
    
    "services_detail": {
        "voice_and_chat_agents": (
            "Vittoris builds human-grade autonomous voice and chat agents that handle 24/7 inbound and outbound "
            "communications. Key channels include live phone lines (SIP/Twilio/Vapi/Retell), Web Chat widgets, "
            "WhatsApp Business API, Instagram/Facebook Meta Direct, and Google Business Messages. They answer questions, "
            "triage complex customer issues, qualify leads, and directly schedule appointments on your calendar."
        ),
        "client_acquisition": (
            "The Vittoris client acquisition engine is a performance-based system that replaces cold outreach friction "
            "with automated, multi-channel qualification funnels. High-intent prospects are engaged by conversational AI "
            "and placed directly onto your sales team's calendar on a pay-per-qualified-appointment or performance model."
        ),
        "custom_infrastructure": (
            "Custom operational infrastructure connects your proprietary data, internal APIs, CRMs (HubSpot, Salesforce), "
            "and databases (PostgreSQL, MongoDB, Supabase). Vittoris builds automated back-office workflows, document intelligence "
            "pipelines (extracting data from PDFs, invoices, contracts), and autonomous error-handling systems."
        ),
        "diagnostic_audit": (
            "Every engagement starts with a thorough Operational & Workflow Diagnostic. The Vittoris engineering team "
            "audits your existing pipeline leakage, customer drop-off points, and manual labor bottlenecks, delivering "
            "a custom technical architecture roadmap tailored to your ROI targets."
        )
    },

    "faqs": [
        {
            "questions": ["pricing", "cost", "how much", "quote", "rate", "fees"],
            "answer": (
                "Vittoris operates primarily on an outcome-driven and performance-based engagement model. "
                "Depending on your requirements (e.g., Pay-Per-Appointment, custom enterprise infrastructure deployment, "
                "or turnkey voice agents), pricing consists of an initial architecture sprint + performance incentives. "
                "You can book a 20-minute Diagnostic & Architecture Consultation directly with our team to get a tailored quote."
            )
        },
        {
            "questions": ["tech stack", "technologies", "integrations", "tools"],
            "answer": (
                "Our architecture integrates seamlessly with modern tech stacks: Python, FastAPI/Flask, Node.js, "
                "LangGraph/CrewAI orchestration, real-time voice streaming (Vapi, Retell AI, ElevenLabs, Deepgram), "
                "telephony (Twilio, Vonage), enterprise CRMs (HubSpot, Salesforce, GoHighLevel), and Cloud infrastructure "
                "(AWS, GCP, Supabase, PostgreSQL, Redis)."
            )
        },
        {
            "questions": ["official intervention", "officials unavailable", "out of office", "after hours", "human intervention"],
            "answer": (
                "When Vittoris officials or lead architects are in client meetings, deploying systems, or out of office, "
                "this autonomous AI agent is authorized to handle 90%+ of operational workflows: booking priority calendar slots, "
                "diagnosing server/service incidents, executing self-healing runbooks, or autonomously compiling an "
                "Executive Incident Dossier and dispatching an emergency escalation ticket to our on-call engineers."
            )
        },
        {
            "questions": ["security", "privacy", "hipaa", "gdpr", "compliance"],
            "answer": (
                "Enterprise security is a core pillar of Vittoris infrastructure. We deploy isolated client instances, "
                "enforce end-to-end TLS 1.3 encryption, role-based access control (RBAC), SOC-2 compliant cloud configurations, "
                "and ensure zero proprietary data leaks across model providers."
            )
        }
    ]
}


def search_knowledge_base(query: str) -> str:
    """Matches user query against Vittoris AI knowledge base."""
    query_lower = query.lower()
    
    # Check FAQs
    for faq in VITTORIS_KNOWLEDGE["faqs"]:
        for trigger in faq["questions"]:
            if trigger in query_lower:
                return faq["answer"]
                
    # Check specific services
    if any(k in query_lower for k in ["voice", "call", "chat", "bot", "whatsapp", "phone"]):
        return VITTORIS_KNOWLEDGE["services_detail"]["voice_and_chat_agents"]
    if any(k in query_lower for k in ["lead", "acquisition", "pay per appointment", "sales"]):
        return VITTORIS_KNOWLEDGE["services_detail"]["client_acquisition"]
    if any(k in query_lower for k in ["infrastructure", "pipeline", "document", "pdf", "invoice"]):
        return VITTORIS_KNOWLEDGE["services_detail"]["custom_infrastructure"]
    if any(k in query_lower for k in ["audit", "diagnostic", "roadmap", "strategy"]):
        return VITTORIS_KNOWLEDGE["services_detail"]["diagnostic_audit"]
        
    # Default to company overview
    return VITTORIS_KNOWLEDGE["company_overview"]

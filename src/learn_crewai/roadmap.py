"""
The Learning Hub - CrewAI Pedagogical Mastery Roadmap.
7-Stage progression covering multi-agent roles, task contexts, enterprise memory, and Flows.
"""

from typing import List, Dict, Any

CREWAI_STAGES: List[Dict[str, Any]] = [
    {
        "stage_number": 1,
        "title": "Multi-Agent Systems Architecture & Core Primitives",
        "domain_focus": "Autonomous agent roles, goals, backstories, task specifications, and sequential execution.",
        "completed": True,
        "key_topics": ["Agent Role & Backstory", "Task Expected Output", "Process.sequential", "Crew Kickoff Protocol"]
    },
    {
        "stage_number": 2,
        "title": "Advanced Agent Design, Delegation & Human-in-the-Loop",
        "domain_focus": "Peer-to-peer delegation, manager agents, Process.hierarchical, and human review approvals.",
        "completed": True,
        "key_topics": ["allow_delegation", "Manager Agent Architecture", "Human Input Injection", "Consensus Building"]
    },
    {
        "stage_number": 3,
        "title": "Task Engineering, Context Flow & Structured Outputs",
        "domain_focus": "Context passing between upstream/downstream tasks, Pydantic schemas, and JSON outputs.",
        "completed": True,
        "key_topics": ["Task Context Pipelines", "output_pydantic & output_json", "Async Tasks", "Guardrail Validations"]
    },
    {
        "stage_number": 4,
        "title": "Tool Orchestration & Custom Tool Development",
        "domain_focus": "@tool decorator, BaseTool subclassing, schema validation, and error recovery handling.",
        "completed": True,
        "key_topics": ["@tool Decorator", "Dynamic Tool Dispatch", "Pydantic Args Validation", "Tool Error Recovery"]
    },
    {
        "stage_number": 5,
        "title": "Enterprise 4-Tier Memory Systems & Knowledge Graphs",
        "domain_focus": "Short-term, Long-term, Entity, and Contextual memories with embedding vector stores.",
        "completed": True,
        "key_topics": ["ShortTermMemory (Chroma)", "LongTermMemory (SQLite)", "EntityMemory (RAG)", "Cross-Crew State Sharing"]
    },
    {
        "stage_number": 6,
        "title": "CrewAI Flows, Production Architecture & Monitoring",
        "domain_focus": "Event-driven Flow state machines, @start and @listen decorators, router branches, and OpenTelemetry.",
        "completed": True,
        "key_topics": ["CrewAI Flows", "@start & @listen", "Stateful Branching", "AgentOps & Langfuse Tracing"]
    },
    {
        "stage_number": 7,
        "title": "Production API Reference & 50 Staff-Level Interview Questions",
        "domain_focus": "Staff architecture trade-offs, token economics, latency reduction, and production deployment.",
        "completed": True,
        "key_topics": ["Multi-Agent Token Overhead", "Deadlock Prevention", "Sub-Agent Isolation", "Enterprise Production Readiness"]
    }
]

def get_completed_count() -> int:
    return sum(1 for s in CREWAI_STAGES if s["completed"])

def get_progress_percentage() -> int:
    return round((get_completed_count() / len(CREWAI_STAGES)) * 100)

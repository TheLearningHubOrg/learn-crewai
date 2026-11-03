"""Custom tools the researcher agent may call.

GlossaryTool is a BaseTool subclass with an args_schema, the pattern to use
whenever a tool takes structured arguments. It reads from an in-process
dictionary so the starter runs without network access.
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

GLOSSARY: dict[str, str] = {
    "agent": "An LLM-backed worker defined by a role, a goal and a backstory, with optional tools.",
    "task": "A unit of work with a description, an expected_output and one responsible agent.",
    "crew": "A group of agents and tasks run under a process (sequential or hierarchical).",
    "process": "The scheduling strategy of a crew: sequential runs tasks in list order, "
    "hierarchical lets a manager agent assign and review work.",
    "guardrail": "A function or LLM check that validates a task output and can send it back for a retry.",
    "flow": "An event-driven workflow class whose methods are wired with @start, @listen and @router.",
    "tool": "A callable an agent may invoke; its name, description and argument schema are shown to the LLM.",
    "context": "The list of upstream tasks whose outputs are injected into a task's prompt.",
}


class GlossaryInput(BaseModel):
    """Arguments the LLM must supply when it calls the glossary tool."""

    term: str = Field(description="A single CrewAI term, for example 'crew' or 'guardrail'.")


class GlossaryTool(BaseTool):
    name: str = "glossary_lookup"
    description: str = (
        "Look up the definition of a CrewAI term. Returns the definition, or a list of "
        "known terms when the term is unknown."
    )
    args_schema: type[BaseModel] = GlossaryInput

    def _run(self, term: str) -> str:
        key = term.strip().lower().rstrip("s")
        if key in GLOSSARY:
            return f"{key}: {GLOSSARY[key]}"
        # Returning guidance instead of raising lets the agent recover on its next step.
        known = ", ".join(sorted(GLOSSARY))
        return f"Unknown term '{term}'. Known terms: {known}."

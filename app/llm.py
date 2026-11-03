"""LLM selection for the starter project.

MODEL=offline (the default) uses OfflineLLM, a deterministic BaseLLM subclass that
never touches the network. Tests, CI and the Docker smoke test use it. Any other
value is passed to crewai.LLM, for example MODEL=openai/gpt-4.1-mini with
OPENAI_API_KEY set, or MODEL=anthropic/claude-sonnet-4-5 with ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from crewai import LLM, BaseLLM
from pydantic import Field

TOPIC_LINE = re.compile(r"^Topic:\s*(.+)$", re.MULTILINE)
AUDIENCE_LINE = re.compile(r"^Audience:\s*(.+)$", re.MULTILINE)
TOOL_CALL = 'Action Input: {"term": "task"}'


def _flatten(messages: str | list[dict[str, Any]]) -> str:
    if isinstance(messages, str):
        return messages
    return "\n".join(str(m.get("content", "")) for m in messages)


class OfflineLLM(BaseLLM):
    """A scripted model: reads the Topic/Audience lines from the prompt and answers
    in the ReAct format the CrewAI agent executor parses."""

    use_tool: bool = True
    prompts: list[str] = Field(default_factory=list)

    def __init__(self, **data: Any) -> None:
        # BaseLLM validates that a model name is present before field defaults apply.
        data.setdefault("model", "offline")
        super().__init__(**data)

    def call(
        self,
        messages: str | list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        callbacks: list[Any] | None = None,
        available_functions: dict[str, Any] | None = None,
        from_task: Any | None = None,
        from_agent: Any | None = None,
        response_model: Any | None = None,
    ) -> str:
        prompt = _flatten(messages)
        self.prompts.append(prompt)
        reply = self._reply(prompt, from_agent, response_model)
        # Real providers report usage from the API response. Estimate it (4 chars per
        # token) so CrewOutput.token_usage is non-zero in tests, as it is in production.
        self._track_token_usage_internal(
            {
                "prompt_tokens": len(prompt) // 4,
                "completion_tokens": len(reply) // 4,
                "total_tokens": (len(prompt) + len(reply)) // 4,
            }
        )
        return reply

    def _reply(self, prompt: str, from_agent: Any, response_model: Any) -> str:
        topic = _last(TOPIC_LINE, prompt, "CrewAI")
        audience = _last(AUDIENCE_LINE, prompt, "engineers")
        role = getattr(from_agent, "role", "") or ""

        if "Writer" in role:
            brief = json.dumps(
                {
                    "topic": topic,
                    "headline": f"{topic}: what {audience} need to know"[:120],
                    "key_points": [
                        f"{topic} is configured in code or YAML and versioned with the app.",
                        f"Test {topic} with a fake LLM so runs are fast and repeatable.",
                        f"Watch token usage and latency for {topic} in production.",
                    ],
                    "audience": audience,
                }
            )
            # With output_pydantic set, CrewAI passes response_model and expects the
            # reply to be bare JSON (no Thought/Final Answer wrapper).
            if response_model is not None:
                return brief
            return "Thought: I can write the brief now.\nFinal Answer: " + brief

        # Researcher: call the glossary tool once, then answer using the observation.
        # The executor appends our previous reply to the messages, so TOOL_CALL in the
        # prompt means the tool already ran.
        if self.use_tool and TOOL_CALL not in prompt:
            return f"Thought: I should check the glossary first.\nAction: glossary_lookup\n{TOOL_CALL}"
        return (
            "Thought: I have enough material.\n"
            f"Final Answer: Research notes on {topic} for {audience}:\n"
            f"- {topic} sits on the Agent, Task and Crew primitives.\n"
            "- Each task states an expected_output that a reviewer can check.\n"
            "- Outputs flow downstream through task context."
        )

    def supports_function_calling(self) -> bool:
        return False

    def supports_stop_words(self) -> bool:
        return False

    def get_context_window_size(self) -> int:
        return 32_000


def _last(pattern: re.Pattern[str], text: str, default: str) -> str:
    found = pattern.findall(text)
    return found[-1].strip() if found else default


def make_llm(model: str | None = None) -> BaseLLM:
    """Return the LLM named by MODEL (or the argument)."""
    name = model or os.getenv("MODEL", "offline")
    if name == "offline":
        return OfflineLLM()
    return LLM(model=name, temperature=float(os.getenv("TEMPERATURE", "0.2")))

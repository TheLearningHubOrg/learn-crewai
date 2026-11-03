"""The briefing crew: a researcher and a writer run in sequence.

Agents and tasks are declared in app/config/*.yaml. This module adds what YAML
cannot express: the LLM instance, tools, the Pydantic output model and the guardrail.
"""

from collections.abc import Callable
from typing import Any

from crewai import Agent, BaseLLM, Crew, Process, Task, TaskOutput
from crewai.project import CrewBase, agent, crew, task
from pydantic import ValidationError

from app.schemas import Brief
from app.tools import GlossaryTool


def validate_brief(output: TaskOutput) -> tuple[bool, Any]:
    """Guardrail for brief_task.

    CrewAI inspects this return annotation at runtime, so this module must not use
    `from __future__ import annotations` (it would turn the annotation into a string).

    Return (True, value) to accept the output, or (False, "reason") to send the
    reason back to the agent, which then retries the task (up to guardrail_max_retries).
    """
    brief = output.pydantic
    if not isinstance(brief, Brief):
        # Guardrails can run before CrewAI converts the raw text to output_pydantic,
        # so parse the raw output ourselves when no model instance is attached yet.
        try:
            brief = Brief.model_validate_json(output.raw)
        except ValidationError as exc:
            return False, f"Return a JSON object that matches the Brief schema: {exc.errors()[0]['msg']}"
    too_long = [p for p in brief.key_points if len(p) > 200]
    if too_long:
        return False, f"Each key point must be under 200 characters; {len(too_long)} are longer."
    # Returning a string makes CrewAI store it as raw and convert it to output_pydantic.
    # Returning the TaskOutput unchanged would skip that conversion.
    return True, brief.model_dump_json()


@CrewBase
class BriefingCrew:
    """Builds a fresh Crew per call. Crew and Task objects keep run state, so do
    not share one instance between concurrent requests.

    Each agent gets its own LLM from llm_factory. LLM objects count tokens
    cumulatively and Crew.token_usage sums them per agent, so one shared
    instance would be counted once per agent that uses it.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, llm_factory: Callable[[], BaseLLM], verbose: bool = False) -> None:
        self.llm_factory = llm_factory
        self.verbose = verbose

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            llm=self.llm_factory(),
            tools=[GlossaryTool()],
            allow_delegation=False,
            max_iter=5,
            verbose=self.verbose,
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],
            llm=self.llm_factory(),
            allow_delegation=False,
            max_iter=3,
            verbose=self.verbose,
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def brief_task(self) -> Task:
        return Task(
            config=self.tasks_config["brief_task"],
            output_pydantic=Brief,
            guardrail=validate_brief,
            guardrail_max_retries=2,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self.verbose,
        )

from crewai import Process, TaskOutput

from app.crew import BriefingCrew, validate_brief
from app.llm import OfflineLLM
from app.schemas import Brief


class Recorder:
    """LLM factory that remembers every OfflineLLM it hands out."""

    def __init__(self):
        self.made: list[OfflineLLM] = []

    def __call__(self) -> OfflineLLM:
        llm = OfflineLLM()
        self.made.append(llm)
        return llm

    @property
    def prompts(self) -> list[str]:
        return [p for llm in self.made for p in llm.prompts]


def run(topic="task guardrails", audience="SREs"):
    recorder = Recorder()
    crew = BriefingCrew(llm_factory=recorder).crew()
    return recorder, crew, crew.kickoff(inputs={"topic": topic, "audience": audience})


def test_crew_shape():
    crew = BriefingCrew(llm_factory=OfflineLLM).crew()
    assert crew.process == Process.sequential
    assert [a.role.strip() for a in crew.agents] == ["CrewAI Research Analyst", "Technical Brief Writer"]
    assert len(crew.tasks) == 2
    assert crew.tasks[1].context == [crew.tasks[0]]


def test_kickoff_returns_structured_brief():
    _, _, result = run()
    assert isinstance(result.pydantic, Brief)
    assert result.pydantic.topic == "task guardrails"
    assert result.pydantic.audience == "SREs"
    assert 3 <= len(result.pydantic.key_points) <= 5


def test_inputs_are_interpolated_and_context_flows():
    llm, _, result = run(topic="flows")
    writer_prompts = [p for p in llm.prompts if "Technical Brief Writer" in p]
    assert writer_prompts, "writer agent was never called"
    # The researcher's notes are injected into the writer's prompt via context.
    assert "Research notes on flows" in writer_prompts[-1]
    assert len(result.tasks_output) == 2


def test_researcher_used_the_tool():
    llm, _, _ = run()
    assert any("Observation:" in p and "task: A unit of work" in p for p in llm.prompts)


def test_guardrail_rejects_long_points():
    long_point = "x" * 250
    brief = Brief(topic="t", headline="h", key_points=[long_point, "b", "c"], audience="a")
    output = TaskOutput(description="d", agent="writer", raw=brief.model_dump_json(), pydantic=brief)
    ok, reason = validate_brief(output)
    assert ok is False
    assert "200 characters" in reason


def test_guardrail_accepts_valid_brief():
    brief = Brief(topic="t", headline="h", key_points=["a", "b", "c"], audience="a")
    output = TaskOutput(description="d", agent="writer", raw=brief.model_dump_json(), pydantic=brief)
    assert validate_brief(output)[0] is True


def test_guardrail_parses_raw_when_no_model_attached():
    # Guardrails run before CrewAI attaches output.pydantic, so raw JSON must be enough.
    raw = Brief(topic="t", headline="h", key_points=["a", "b", "c"], audience="a").model_dump_json()
    assert validate_brief(TaskOutput(description="d", agent="writer", raw=raw))[0] is True


def test_guardrail_rejects_non_json():
    ok, reason = validate_brief(TaskOutput(description="d", agent="writer", raw="Sure! Here is the brief."))
    assert ok is False
    assert "Brief schema" in reason


def test_writer_called_once_when_output_is_valid():
    llm, _, _ = run()
    writer_calls = [p for p in llm.prompts if "Technical Brief Writer" in p]
    assert len(writer_calls) == 1, "a guardrail retry happened"


def test_token_usage_is_reported():
    _, _, result = run()
    assert result.token_usage.total_tokens > 0
    # researcher: tool call + final answer; writer: one structured answer
    assert result.token_usage.successful_requests == 3


def test_each_agent_has_its_own_llm():
    crew = BriefingCrew(llm_factory=OfflineLLM).crew()
    researcher, writer = crew.agents
    assert researcher.llm is not writer.llm

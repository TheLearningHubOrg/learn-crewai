"""
The Learning Hub - CrewAI Multi-Agent Autonomous Orchestration Engine CLI.
Demonstrates role-playing agents, task context chaining, tools, 4-tier memory, and Flows.
"""

from __future__ import annotations
import sys
from .roadmap import CREWAI_STAGES, get_completed_count, get_progress_percentage
from .crew import (
    Agent,
    Task,
    Crew,
    Process,
    tool,
    Flow,
    start,
    listen
)


def print_banner() -> None:
    print("=" * 76)
    print("   THE LEARNING HUB: CREWAI MULTI-AGENT AUTONOMOUS ORCHESTRATION ENGINE   ")
    print("=" * 76)


def display_roadmap() -> None:
    print("\n[+] 7-Stage CrewAI Pedagogical Mastery Roadmap:")
    for stage in CREWAI_STAGES:
        status = "[DONE]" if stage["completed"] else "[TODO]"
        print(f"  {status} Stage {stage['stage_number']}: {stage['title']}")
        print(f"         Focus: {stage['domain_focus']}")
    print(f"\nProgress: {get_completed_count()}/{len(CREWAI_STAGES)} Stages Complete ({get_progress_percentage()}%)\n")


@tool("benchmark_database", description="Retrieves enterprise throughput metrics for vector databases.")
def query_benchmark_tool(query: str) -> str:
    return f"Benchmark verified: Pinecone/Qdrant achieve 14,500 QPS with p99 latency under 12ms."


def demonstrate_multi_agent_crew() -> None:
    print("-" * 68)
    print("1. Multi-Agent Autonomous Team (Process.sequential)")
    print("-" * 68)

    # 1. Define Specialized Agents
    researcher = Agent(
        role="Principal AI Research Analyst",
        goal="Discover and validate scalable multi-agent enterprise deployment patterns",
        backstory="World-class AI systems researcher with 12 published papers on agent consensus.",
        tools=[query_benchmark_tool],
        verbose=True,
    )

    architect = Agent(
        role="Staff Cloud Infrastructure Architect",
        goal="Design resilient Kubernetes topologies for agentic serving with zero-downtime",
        backstory="Ex-hyperscaler architect specialized in distributed consensus and P99 latency tuning.",
        verbose=True,
    )

    writer = Agent(
        role="Executive Technical Communicator",
        goal="Distill deep technical architectures into high-impact executive briefs",
        backstory="Former technical editor for top enterprise publications.",
        verbose=True,
    )

    # 2. Define Tasks with Context Pipelines
    task1 = Task(
        description="Analyze scalable agent architectures and check benchmark_database for vector throughput.",
        expected_output="Detailed architectural analysis of vector indexing throughput.",
        agent=researcher,
    )

    task2 = Task(
        description="Design high-availability Kubernetes multi-cluster topology based on the research findings.",
        expected_output="Infrastructure topology specification.",
        agent=architect,
        context=[task1],  # Chained context from Task 1
    )

    task3 = Task(
        description="Synthesize an executive summary of the architecture and infrastructure decisions.",
        expected_output="One-page executive briefing.",
        agent=writer,
        context=[task2],  # Chained context from Task 2
    )

    # 3. Assemble and Kickoff Crew
    crew = Crew(
        agents=[researcher, architect, writer],
        tasks=[task1, task2, task3],
        process=Process.SEQUENTIAL,
        memory=True,
    )

    print("  [+] Kicking off Crew with 3 autonomous agents...")
    output = crew.kickoff()

    print("\n  [Execution Outputs by Task]:")
    for item in output.tasks_output:
        print(f"    - Task {item['task_index'] + 1} [{item['agent']}]:")
        print(f"      Output: {item['output'][:90]}...")

    print(f"\n  [Telemetry]: Total Tokens Consumed: {output.token_usage['total_tokens']}")

    # Inspect 4-tier memory
    if crew.entity_memory:
        entities = crew.entity_memory.get_top_entities(top_n=4)
        print(f"  [Entity Memory Indexed]: {entities}\n")


def demonstrate_hierarchical_crew() -> None:
    print("-" * 68)
    print("2. Hierarchical Multi-Agent Crew (Process.hierarchical)")
    print("-" * 68)

    dev_lead = Agent(
        role="Lead Systems Engineer",
        goal="Implement mission-critical distributed consensus modules",
        backstory="Distributed systems hacker specialized in Raft and Paxos.",
    )

    task_consensus = Task(
        description="Implement leader election failover logic with 250ms lease heartbeat.",
        expected_output="Consensus module code specification.",
        agent=dev_lead,
    )

    crew_hierarchical = Crew(
        agents=[dev_lead],
        tasks=[task_consensus],
        process=Process.HIERARCHICAL,
        memory=True,
    )

    print("  [+] Kicking off Hierarchical Crew with automated Manager Agent...")
    res = crew_hierarchical.kickoff()
    print(f"  [Manager Result]: {res.raw[:120]}...\n")


class EnterpriseDeploymentFlow(Flow):
    """Demonstrates event-driven CrewAI Flow orchestrating pipeline stages."""

    @start
    def validate_inputs(self) -> str:
        print("    [Flow @start] Validating environmental configuration and API credentials...")
        return "CONFIG_VALIDATED"

    @listen("validate_inputs")
    def trigger_agent_rollout(self, status: str) -> str:
        print(f"    [Flow @listen] Received status: '{status}' -> Triggering autonomous agent deployment...")
        return "DEPLOYMENT_ACTIVE_SUCCESS"


def demonstrate_flow() -> None:
    print("-" * 68)
    print("3. Event-Driven CrewAI Flows (@start & @listen)")
    print("-" * 68)

    flow = EnterpriseDeploymentFlow()
    result = flow.kickoff()
    print(f"  [Flow Result]: {result}\n")


def main() -> None:
    print_banner()
    display_roadmap()
    demonstrate_multi_agent_crew()
    demonstrate_hierarchical_crew()
    demonstrate_flow()
    print("=" * 76)
    print("   CREWAI PRODUCTION MULTI-AGENT DEMO COMPLETED SUCCESSFULLY   ")
    print("=" * 76)


if __name__ == "__main__":
    main()

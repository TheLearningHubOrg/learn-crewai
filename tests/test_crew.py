"""
Unit test suite for the CrewAI Multi-Agent Autonomous Orchestration Engine.
Tests cover Agent execution, Task context flow, Tools, Memory tiers, Hierarchical crews, and Flows.
"""

import unittest
from src.learn_crewai.crew import (
    Agent,
    Task,
    Crew,
    Process,
    CrewOutput,
    BaseTool,
    tool,
    ShortTermMemory,
    LongTermMemory,
    EntityMemory,
    Flow,
    start,
    listen
)
from src.learn_crewai.roadmap import (
    CREWAI_STAGES,
    get_completed_count,
    get_progress_percentage
)


class TestCrewAIEngine(unittest.TestCase):

    def setUp(self):
        @tool("math_tool", description="Calculates math.")
        def math_tool(expr: str) -> str:
            return "42"

        self.math_tool = math_tool
        self.agent1 = Agent(
            role="Research Analyst",
            goal="Analyze AI market trends",
            backstory="Experienced technology researcher",
            tools=[self.math_tool],
            memory=True,
        )

    def test_agent_task_execution_with_tool(self):
        task = Task(
            description="Use math_tool to compute token budget",
            expected_output="Computed budget",
            agent=self.agent1
        )
        output = task.execute()
        self.assertIn("Research Analyst", output)
        self.assertIn("Used math_tool: 42", output)

    def test_task_context_chaining(self):
        agent2 = Agent(
            role="Editor",
            goal="Refine technical reports",
            backstory="Professional editor"
        )
        task1 = Task(
            description="Generate baseline facts",
            expected_output="Facts report",
            agent=self.agent1
        )
        task1.execute()

        task2 = Task(
            description="Edit baseline facts",
            expected_output="Final edit",
            agent=agent2,
            context=[task1]
        )
        out2 = task2.execute()
        self.assertIn("Editor", out2)
        self.assertIn("Edit baseline facts", out2)

    def test_sequential_crew_kickoff(self):
        t1 = Task(description="Step 1 analysis", expected_output="Out 1", agent=self.agent1)
        crew = Crew(
            agents=[self.agent1],
            tasks=[t1],
            process=Process.SEQUENTIAL,
            memory=True
        )
        output = crew.kickoff()
        self.assertIsInstance(output, CrewOutput)
        self.assertEqual(len(output.tasks_output), 1)
        self.assertIn("Step 1 analysis", output.raw)

    def test_hierarchical_crew_with_manager(self):
        t1 = Task(description="Implement critical microservice", expected_output="Microservice spec", agent=self.agent1)
        crew = Crew(
            agents=[self.agent1],
            tasks=[t1],
            process=Process.HIERARCHICAL,
            memory=True
        )
        output = crew.kickoff()
        self.assertIn("Manager", output.raw)
        self.assertIn("Research Analyst", output.raw)

    def test_memory_systems(self):
        short_mem = ShortTermMemory()
        short_mem.save("Tester", "Message A")
        short_mem.save("Tester", "Message B")
        ctx = short_mem.get_context()
        self.assertIn("Message A", ctx)
        self.assertIn("Message B", ctx)

        long_mem = LongTermMemory()
        long_mem.put("cluster_id", "prod-west-2")
        self.assertEqual(long_mem.get("cluster_id"), "prod-west-2")

        entity_mem = EntityMemory()
        entity_mem.extract_and_store("Kubernetes and Docker run inside AWS Cloud.")
        top_entities = [e[0] for e in entity_mem.get_top_entities()]
        self.assertTrue(any(item in top_entities for item in ["Kubernetes", "Docker", "AWS"]))

    def test_flow_event_chain(self):
        class SampleFlow(Flow):
            @start
            def step_one(self):
                return "ONE"

            @listen("step_one")
            def step_two(self, prev):
                return f"{prev}->TWO"

        flow = SampleFlow()
        res = flow.kickoff()
        self.assertEqual(res, "ONE->TWO")

    def test_roadmap_7_stages(self):
        self.assertEqual(len(CREWAI_STAGES), 7)
        self.assertEqual(get_completed_count(), 7)
        self.assertEqual(get_progress_percentage(), 100)


if __name__ == "__main__":
    unittest.main()

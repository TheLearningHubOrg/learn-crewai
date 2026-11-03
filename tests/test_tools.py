from app.tools import GlossaryTool


def test_known_term_returns_definition():
    result = GlossaryTool().run(term="Crew")
    assert result.startswith("crew: ")


def test_plural_is_normalised():
    assert GlossaryTool().run(term="tasks").startswith("task: ")


def test_unknown_term_lists_known_terms():
    result = GlossaryTool().run(term="blockchain")
    assert "Unknown term 'blockchain'" in result
    assert "guardrail" in result


def test_schema_is_exposed_to_the_llm():
    schema = GlossaryTool().args_schema.model_json_schema()
    assert schema["required"] == ["term"]

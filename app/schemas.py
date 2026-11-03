"""Pydantic models shared by the crew (structured task output) and the HTTP API."""

from pydantic import BaseModel, Field


class Brief(BaseModel):
    """The structured deliverable produced by the writer agent."""

    topic: str = Field(description="The topic the brief covers, copied from the input.")
    headline: str = Field(description="One-line headline, at most 120 characters.", max_length=120)
    key_points: list[str] = Field(
        description="Three to five standalone points, each one sentence.",
        min_length=3,
        max_length=5,
    )
    audience: str = Field(description="Who the brief is written for.")


class BriefRequest(BaseModel):
    """Body of POST /briefs."""

    topic: str = Field(min_length=3, max_length=200, examples=["task guardrails"])
    audience: str = Field(default="backend engineers", min_length=3, max_length=80)


class Usage(BaseModel):
    """Token accounting copied from CrewOutput.token_usage."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0


class BriefResponse(BaseModel):
    """Body returned by POST /briefs."""

    brief: Brief
    research_notes: str
    usage: Usage

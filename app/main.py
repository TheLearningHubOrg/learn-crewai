"""HTTP API around the briefing crew.

Run locally:   uvicorn app.main:app --reload --port 8000
Run the crew:  python -m app.cli "task guardrails"
"""

from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI, HTTPException

from app.crew import BriefingCrew
from app.llm import make_llm
from app.schemas import Brief, BriefRequest, BriefResponse, Usage

app = FastAPI(title="learn-crewai briefing service", version="1.0.0")

# Caps concurrent crew runs so a burst of requests cannot exhaust the LLM rate limit.
_RUNS = asyncio.Semaphore(int(os.getenv("MAX_CONCURRENT_RUNS", "4")))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": os.getenv("MODEL", "offline")}


@app.post("/briefs", response_model=BriefResponse)
async def create_brief(request: BriefRequest) -> BriefResponse:
    crew = BriefingCrew(llm_factory=make_llm).crew()
    inputs = {"topic": request.topic, "audience": request.audience}
    async with _RUNS:
        # kickoff() blocks on LLM I/O; run it in a worker thread so the event loop
        # keeps serving /health and other requests.
        result = await asyncio.to_thread(crew.kickoff, inputs=inputs)

    if not isinstance(result.pydantic, Brief):
        raise HTTPException(status_code=502, detail="Crew did not return a valid Brief.")

    usage = result.token_usage
    return BriefResponse(
        brief=result.pydantic,
        research_notes=result.tasks_output[0].raw,
        usage=Usage(
            total_tokens=usage.total_tokens,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            successful_requests=usage.successful_requests,
        ),
    )

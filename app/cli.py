"""Command-line entry point: python -m app.cli "<topic>" [--audience "..."] [--verbose]"""

from __future__ import annotations

import argparse

from app.crew import BriefingCrew
from app.llm import make_llm


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the briefing crew once.")
    parser.add_argument("topic")
    parser.add_argument("--audience", default="backend engineers")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    crew = BriefingCrew(llm_factory=make_llm, verbose=args.verbose).crew()
    result = crew.kickoff(inputs={"topic": args.topic, "audience": args.audience})

    brief = result.pydantic
    print(brief.model_dump_json(indent=2) if brief else result.raw)
    print(f"tokens used: {result.token_usage.total_tokens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

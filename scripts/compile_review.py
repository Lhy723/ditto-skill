from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.common import PHASE_ORDER, parse_key_value_bullets, write_json
except ImportError:  # pragma: no cover - direct script execution path
    from common import PHASE_ORDER, parse_key_value_bullets, write_json


VALID_DECISIONS = {"keep", "drop"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", required=True)
    parser.add_argument("--draft", default="reviewed-milestones.md")
    parser.add_argument("--output", default="reviewed-milestones.json")
    return parser.parse_args()


def require_fields(block: dict[str, object], fields: list[str]) -> None:
    missing = [field for field in fields if field not in block]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def reject_todo(value: str, field: str) -> str:
    stripped = value.strip()
    if stripped == "TODO" or stripped.startswith("TODO"):
        raise ValueError(f"Field '{field}' still contains TODO")
    return stripped


def main() -> None:
    args = parse_args()
    analysis_dir = Path(args.analysis_dir)
    draft_path = analysis_dir / args.draft
    output_path = analysis_dir / args.output
    lines = draft_path.read_text().splitlines()

    if not lines or not lines[0].startswith("# Reviewed Milestones Draft:"):
        raise ValueError("Draft must start with '# Reviewed Milestones Draft: <repo-slug>'")

    milestones: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        if lines[index].strip() == "## Milestone":
            block, index = parse_key_value_bullets(lines, index + 1)
            require_fields(
                block,
                [
                    "sha",
                    "message",
                    "decision",
                    "phase",
                    "capability",
                    "constraint_or_tradeoff",
                    "why",
                    "evidence_refs",
                ],
            )
            decision = str(block["decision"]).strip()
            phase = str(block["phase"]).strip()
            if decision not in VALID_DECISIONS:
                raise ValueError(f"Invalid decision '{decision}'")
            if phase not in PHASE_ORDER:
                raise ValueError(f"Invalid phase '{phase}'")
            evidence_refs = block["evidence_refs"]
            if not isinstance(evidence_refs, list):
                raise ValueError("evidence_refs must be a list")
            milestones.append(
                {
                    "sha": str(block["sha"]).strip(),
                    "message": str(block["message"]).strip(),
                    "decision": decision,
                    "phase": phase,
                    "capability": reject_todo(str(block["capability"]), "capability"),
                    "constraint_or_tradeoff": reject_todo(
                        str(block["constraint_or_tradeoff"]), "constraint_or_tradeoff"
                    ),
                    "why": reject_todo(str(block["why"]), "why"),
                    "evidence_refs": [str(item).strip() for item in evidence_refs],
                    "review_mode": "assistant",
                }
            )
            continue
        index += 1

    if not milestones:
        raise ValueError("No '## Milestone' blocks found in reviewed-milestones.md")

    write_json(output_path, milestones)
    print(str(output_path))


if __name__ == "__main__":
    main()

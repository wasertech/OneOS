"""Trace refinement — propose and apply improvements to trace samples."""

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Refinement:
    """A proposed or applied improvement to a trace."""
    turn_idx: int
    action: str  # "clean_prompt", "remove_errors", "split_turn", "add_missing_tool_result"
    description: str
    before: str = ""
    after: str = ""

    def to_dict(self) -> dict:
        return {
            "turn_idx": self.turn_idx,
            "action": self.action,
            "description": self.description,
            "before": self.before[:300],
            "after": self.after[:300],
        }


@dataclass
class RefinementPlan:
    """Complete refinement plan for a trace."""
    scenario_name: str
    category: str
    source_file: str
    refinements: list[Refinement] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario_name,
            "category": self.category,
            "source_file": self.source_file,
            "num_refinements": len(self.refinements),
            "summary": self.summary,
            "refinements": [r.to_dict() for r in self.refinements],
        }


def _clean_user_prompt(content: str) -> tuple[str, bool]:
    """Clean corrupted user prompts. Returns (cleaned_content, was_modified)."""
    lines = content.strip().split("\n")
    if not lines:
        return "", False

    first = lines[0].strip()
    if len(first) < 200 and ("`" in first or "?" in first or "montre" in first.lower() or "fais" in first.lower()):
        was_modified = "\n".join(lines) != first
        return first, was_modified

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped and i > 0:
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if next_line and any(phrase in next_line.lower() for phrase in [
                    "voulez-vous", "je peux", "voici", "bien sûr", "c'est une",
                    "exception", "error", "traceback"
                ]):
                    result = "\n".join(lines[:i]).strip()
                    was_modified = result != content.strip()
                    return result, was_modified

    return content.strip(), False


def _filter_error_tool_results(results: list[str]) -> tuple[list[str], bool]:
    """Remove tool results that are pure error messages. Returns (kept, modified)."""
    error_markers = ["Exception", "Traceback", "Error:", "Traceback (most recent"]
    kept = []
    modified = False
    for r in results:
        is_error = any(m in r for m in error_markers)
        if not is_error:
            kept.append(r)
        else:
            modified = True
    return kept, modified


def _detect_missing_tool_results(sample, turn_idx: int) -> tuple[list[str], bool]:
    """Detect tool calls without matching results (incomplete turns)."""

    if turn_idx >= len(sample.turns):
        return [], False

    turn = sample.turns[turn_idx]
    missing_count = max(0, len(turn.tool_calls) - len(turn.tool_results))
    if missing_count > 0:
        desc_parts = []
        for tc in turn.tool_calls[len(turn.tool_results):]:
            fn_name = tc.get("function", {}).get("name", "unknown")
            desc_parts.append(f"missing result for {fn_name} call")
        return [f"{missing_count} tool calls without results: {'; '.join(desc_parts)}"], True

    return [], False


def plan_refinements(sample) -> RefinementPlan:
    """Generate a refinement plan for a trace based on detected issues.

    Args:
        sample: TraceSample to refine

    Returns:
        RefinementPlan with proposed changes
    """
    refinements = []

    # Clean corrupted user prompts
    for ti, turn in enumerate(sample.turns):
        cleaned, was_modified = _clean_user_prompt(turn.user_content)
        if was_modified and cleaned != turn.user_content:
            refinements.append(Refinement(
                turn_idx=ti,
                action="clean_prompt",
                description=f"Cleaned corrupted user prompt (removed assistant text leakage)",
                before=turn.user_content[:200],
                after=cleaned[:200],
            ))

    # Filter error tool results
    for ti, turn in enumerate(sample.turns):
        kept, was_modified = _filter_error_tool_results(turn.tool_results)
        if was_modified:
            refinements.append(Refinement(
                turn_idx=ti,
                action="remove_errors",
                description=f"Removed {len(turn.tool_results) - len(kept)} error result(s)",
                before=str(len(turn.tool_results)),
                after=str(len(kept)),
            ))

    # Detect incomplete tool call chains
    for ti in range(len(sample.turns)):
        missing, was_modified = _detect_missing_tool_results(sample, ti)
        if was_modified:
            refinements.append(Refinement(
                turn_idx=ti,
                action="incomplete_tools",
                description=f"Detected {len(missing)} tool call(s) without results",
                before="",
                after=", ".join(missing),
            ))

    summary = f"{len(refinements)} refinement(s) proposed for '{sample.scenario_name}'"
    return RefinementPlan(
        scenario_name=sample.scenario_name,
        category=sample.category,
        source_file=sample.source_file,
        refinements=refinements,
        summary=summary,
    )


def apply_refinements(sample, plan: RefinementPlan):
    """Apply all refinements in the plan to a sample (mutates the sample).

    Args:
        sample: TraceSample to modify in-place
        plan: RefinementPlan with actions to apply
    """
    for ref in plan.refinements:
        if ref.turn_idx >= len(sample.turns):
            continue

        turn = sample.turns[ref.turn_idx]

        if ref.action == "clean_prompt":
            # Apply prompt cleaning
            cleaned, _ = _clean_user_prompt(turn.user_content)
            turn.user_content = cleaned

        elif ref.action == "remove_errors":
            # Filter out error tool results
            kept, _ = _filter_error_tool_results(turn.tool_results)
            turn.tool_results = kept

        # Note: "incomplete_tools" is informational only — we flag it but don't auto-fix
        # since we can't generate missing execution results without re-running


def refine_batch(samples) -> list[RefinementPlan]:
    """Generate refinement plans for multiple traces. Returns sorted by #refinements desc."""
    plans = [plan_refinements(s) for s in samples]
    plans.sort(key=lambda p: -p.num_refinements)
    return plans

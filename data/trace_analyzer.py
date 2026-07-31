"""Trace quality analyzer — detect gaps, errors, and improvement opportunities."""

import json
import re
from dataclasses import dataclass, field
from typing import Optional


# ============================================================================
# Data model (re-export from extract_traces for convenience)
# ============================================================================

@dataclass
class Turn:
    user_content: str = ""
    assistant_content: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[str] = field(default_factory=list)


@dataclass
class TraceSample:
    source_file: str = ""
    scenario_name: str = ""
    category: str = "unknown"
    system_prompt: str = ""
    turns: list[Turn] = field(default_factory=list)
    status: str = "pending"


@dataclass
class Gap:
    """A detected quality gap in a trace."""
    turn_idx: int
    severity: str  # "critical", "warning", "info"
    category: str  # "error", "incompleteness", "style", "redundancy"
    description: str
    evidence: str = ""

    def to_dict(self) -> dict:
        return {
            "turn_idx": self.turn_idx,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "evidence": self.evidence[:500],
        }


@dataclass
class AnalysisResult:
    """Complete quality analysis of a trace."""
    sample: TraceSample
    gaps: list[Gap] = field(default_factory=list)
    score: float = 1.0  # 0.0 - 1.0, higher is better
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "scenario": self.sample.scenario_name,
            "category": self.sample.category,
            "source_file": self.sample.source_file,
            "num_turns": len(self.sample.turns),
            "total_tool_calls": sum(len(t.tool_calls) for t in self.sample.turns),
            "score": round(self.score, 3),
            "summary": self.summary,
            "gaps": [g.to_dict() for g in self.gaps],
        }


# ============================================================================
# Gap detection rules
# ============================================================================

def _detect_api_errors(turn: Turn) -> Optional[Gap]:
    """Detect LLM API call failures or infrastructure errors."""
    combined = f"{turn.user_content} {turn.assistant_content}"
    patterns = [
        r"LLM API call failed",
        r"Request timed out",
        r"Connection refused",
        r"429 Too Many Requests",
        r"Rate limit exceeded",
    ]
    for pat in patterns:
        m = re.search(pat, combined, re.IGNORECASE)
        if m:
            return Gap(
                turn_idx=0, severity="critical", category="error",
                description=f"API/infrastructure error detected",
                evidence=m.group(),
            )
    return None


def _detect_error_tool_results(turn: Turn) -> Optional[Gap]:
    """Detect tool execution errors (exceptions, tracebacks)."""
    for result in turn.tool_results:
        error_indicators = ["Exception", "Traceback", "Error:", "Traceback (most recent call last)"]
        for ind in error_indicators:
            if ind in result:
                # Count how many results are errors vs total
                error_count = sum(1 for r in turn.tool_results if any(e in r for e in error_indicators))
                total = len(turn.tool_results)
                severity = "critical" if total > 0 and error_count / total > 0.5 else "warning"
                return Gap(
                    turn_idx=0, severity=severity, category="error",
                    description=f"{error_count}/{total} tool results contain errors",
                    evidence=result[:300],
                )
    return None


def _detect_corrupted_prompts(turn: Turn) -> Optional[Gap]:
    """Detect assistant text leaked into user prompts."""
    indicators = [
        "voici", "bien sûr", "excellente", "merci pour", "c'est une",
        "je peux vous", "je remarque", "très bien !", "personnellement",
        "voudriez-vous", "je vous suggère", "j'ai l'honneur",
    ]
    content_lower = turn.user_content.lower().strip()
    for ind in indicators:
        if content_lower.startswith(ind):
            return Gap(
                turn_idx=0, severity="critical", category="corruption",
                description="User prompt contains assistant-like text (data corruption)",
                evidence=turn.user_content[:200],
            )
    return None


def _detect_too_short(sample: TraceSample) -> Optional[Gap]:
    """Detect traces with insufficient turns for meaningful training."""
    real_turns = sum(1 for t in sample.turns if t.user_content.strip() and len(t.user_content.strip()) > 5)
    total_tool_calls = sum(len(t.tool_calls) for t in sample.turns)
    if real_turns < 2:
        return Gap(
            turn_idx=0, severity="warning", category="incompleteness",
            description=f"Only {real_turns} meaningful turn(s) — insufficient training signal",
        )
    if total_tool_calls == 0 and real_turns > 1:
        return Gap(
            turn_idx=0, severity="info", category="style",
            description="No tool calls in trace — may not teach function-calling patterns",
        )
    return None


def _detect_redundant_tool_calls(sample: TraceSample) -> list[Gap]:
    """Detect repeated identical tool calls (looping behavior)."""
    seen = {}
    gaps = []
    for ti, turn in enumerate(sample.turns):
        for tc in turn.tool_calls:
            code = tc.get("function", {}).get("arguments", "{}")
            if "code" in code:
                try:
                    args = json.loads(code) if isinstance(code, str) else code
                    code_content = args.get("code", "")[:100]  # First 100 chars for dedup
                except (json.JSONDecodeError, TypeError):
                    continue
            else:
                code_content = code[:100]

            key = f"{tc.get('function', {}).get('name', '')}:{code_content}"
            if key in seen and len(key) > 20:  # Only flag substantial repeats
                gaps.append(Gap(
                    turn_idx=ti, severity="warning", category="redundancy",
                    description=f"Repeated tool call (first seen at turn {seen[key]})",
                    evidence=key[:150],
                ))
            else:
                seen[key] = ti
    return gaps


def _detect_empty_assistant_responses(sample: TraceSample) -> list[Gap]:
    """Detect assistant turns with neither content nor tool calls."""
    gaps = []
    for ti, turn in enumerate(sample.turns):
        if not turn.user_content.strip():
            continue  # Skip empty user prompts (they're expected between tool results and next user msg)
        has_content = bool(turn.assistant_content and turn.assistant_content.strip())
        has_tools = len(turn.tool_calls) > 0
        if not has_content and not has_tools:
            gaps.append(Gap(
                turn_idx=ti, severity="warning", category="incompleteness",
                description="Assistant turn with no content and no tool calls (orphan)",
            ))
    return gaps


def _detect_long_response(turn: Turn) -> Optional[Gap]:
    """Detect overly long assistant responses that break 'one line at a time' style."""
    if turn.assistant_content and len(turn.assistant_content) > 2000:
        # Only flag if it's text (not code output)
        return Gap(
            turn_idx=0, severity="info", category="style",
            description=f"Very long assistant response ({len(turn.assistant_content)} chars)",
            evidence=turn.assistant_content[:300],
        )
    return None


# ============================================================================
# Scoring
# ============================================================================

def _compute_score(sample: TraceSample, gaps: list[Gap]) -> float:
    """Compute quality score 0-1 based on detected issues."""
    if not sample.turns:
        return 0.0

    score = 1.0
    for g in gaps:
        if g.severity == "critical":
            score -= 0.3
        elif g.severity == "warning":
            score -= 0.15
        else:
            score -= 0.05

    return max(0.0, min(1.0, score))


def _generate_summary(sample: TraceSample, gaps: list[Gap], score: float) -> str:
    """Generate human-readable summary."""
    parts = []
    criticals = [g for g in gaps if g.severity == "critical"]
    warnings = [g for g in gaps if g.severity == "warning"]
    infos = [g for g in gaps if g.severity == "info"]

    parts.append(f"Score: {score:.0%} | Turns: {len(sample.turns)} | Tool calls: {sum(len(t.tool_calls) for t in sample.turns)}")

    if criticals:
        crit_types = set(g.category for g in criticals)
        parts.append(f"CRITICAL issues ({len(criticals)}) in: {', '.join(crit_types)}")
    elif warnings:
        warn_types = set(g.category for g in warnings)
        parts.append(f"{len(warnings)} warning(s): {', '.join(sorted(warn_types))}")

    if infos:
        parts.append(f"{len(infos)} info note(s)")

    return " | ".join(parts)


# ============================================================================
# Public API
# ============================================================================

def analyze_trace(sample: TraceSample) -> AnalysisResult:
    """Run full quality analysis on a trace. Returns AnalysisResult."""
    gaps = []

    # Per-turn checks
    for turn in sample.turns:
        if gap := _detect_api_errors(turn):
            gaps.append(gap)
        if gap := _detect_error_tool_results(turn):
            gaps.append(gap)
        if gap := _detect_corrupted_prompts(turn):
            gaps.append(gap)
        if gap := _detect_long_response(turn):
            gaps.append(gap)

    # Whole-trace checks
    if gap := _detect_too_short(sample):
        gaps.append(gap)

    gaps.extend(_detect_redundant_tool_calls(sample))
    gaps.extend(_detect_empty_assistant_responses(sample))

    score = _compute_score(sample, gaps)
    summary = _generate_summary(sample, gaps, score)

    return AnalysisResult(
        sample=sample, gaps=gaps, score=score, summary=summary,
    )


def analyze_batch(samples: list[TraceSample]) -> list[AnalysisResult]:
    """Analyze multiple traces. Returns sorted by score ascending (worst first)."""
    results = [analyze_trace(s) for s in samples]
    results.sort(key=lambda r: r.score)
    return results

#!/usr/bin/env python3
"""Run eval tasks through the OneOS simulator and verify traces.

Usage:
    python3 evals/run_eval.py                          # all tasks
    python3 evals/run_eval.py --tasks intro             # specific task file
    python3 evals/run_eval.py --dry-run                 # list tasks, no simulation
    python3 evals/run_eval.py --verify-only <dir/>      # verify existing traces

Output: evals/output/<timestamp>/report.md + traces/
"""
import json, sys, os, time, glob
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent  # src/evals/
OUTPUT_DIR = SCRIPT_DIR / "output"
TASKS_DIR = SCRIPT_DIR / "tasks"

# ── Load task files ──────────────────────────────────────────────────────────

def load_tasks(task_filter: str = None) -> list:
    """Load tasks from evals/tasks/*.jsonl, optionally filtered by task filename."""
    tasks = []
    for fpath in sorted(TASKS_DIR.glob("*.jsonl")):
        name = fpath.stem
        if task_filter and task_filter not in name:
            continue
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                task = json.loads(line)
                task["_source"] = name
                tasks.append(task)
    return tasks


# ── Run single task through simulator ────────────────────────────────────────

def run_task(task: dict, sim, trace_dir: Path) -> dict:
    """Run one eval task through the simulator. Returns result dict."""
    from scenarios import Scenario, Turn

    task_id = task["id"]
    turns = [Turn(prompt=t) for t in task.get("turns", [])]
    scenario = Scenario(
        name=f"eval_{task_id}",
        category=task.get("category", "eval"),
        turns=turns,
        description=task.get("description", ""),
    )

    print(f"\n{'='*60}")
    print(f"Task: {task_id} ({task.get('category','?')})")
    print(f"Turns: {len(turns)}")

    try:
        trace_path = sim.run_scenario(scenario)
        if trace_path:
            # copy trace to eval output directory
            src = Path(trace_path).expanduser()
            if src.exists():
                dst = trace_dir / src.name
                import shutil
                shutil.copy2(src, dst)
                print(f"  → trace @ {dst}")
                return {"task": task, "trace_file": str(dst), "success": True}
            else:
                print(f"  ⚠️ simulator returned path but file not found: {trace_path}")
                return {"task": task, "trace_file": None, "success": False, "error": "trace not found"}
        else:
            print(f"  ⚠️ simulator returned no trace path")
            return {"task": task, "trace_file": None, "success": False, "error": "no trace returned"}
    except Exception as e:
        print(f"  ❌ error: {e}")
        return {"task": task, "trace_file": None, "success": False, "error": str(e)}


# ── Verify traces ────────────────────────────────────────────────────────────

def verify_traces(trace_dir: Path, verbose: bool = False) -> list:
    """Run verify_trace.py on all traces in directory."""
    # Import verify_trace module
    sys.path.insert(0, str(SCRIPT_DIR))
    import verify_trace as vt

    results = []
    for fpath in sorted(trace_dir.glob("*.jsonl")):
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if line:
                    trace = json.loads(line)
                    r = vt.verify_trace(trace, verbose=verbose)
                    results.append(r)
    return results


# ── Generate report ──────────────────────────────────────────────────────────

def generate_report(results: list, output_path: Path):
    """Write markdown report with per-task results + aggregate scores."""
    lines = [
        f"# Eval Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**Tasks evaluated:** {len(results)}",
        "",
    ]

    # Per-task results
    for r in results:
        meta = r.get("_meta", {})
        score = meta.get("overall_score", 0)
        check_str = f"{meta.get('checks_passed',0)}/{meta.get('checks_total',0)}"
        lines.append(f"## {meta.get('scenario','?')} ({meta.get('category','?')})")
        lines.append(f"**Score: {score:.0%}** ({check_str})")
        lines.append(f"| Check | Status | Detail |")
        lines.append(f"|---|---|---|")
        for key in sorted(r.keys()):
            if key.startswith("T") and "_" in key:
                v = r[key]
                mark = "✅" if v.get("pass") else "⚠️"
                detail = v.get("detail", "")
                lines.append(f"| **{key}** | {mark} | {detail} |")
        lines.append("")

    # Aggregate scores
    lines.append("## Aggregate")
    lines.append("| Check | Pass Rate |")
    lines.append("|---|---|")
    check_names = [k for k in sorted(r.keys()) if k.startswith("T") and "_" in k]
    for ck in check_names:
        total = len(results)
        passed = sum(1 for r in results if r.get(ck, {}).get("pass"))
        lines.append(f"| **{ck}** | {passed}/{total} = {passed/total:.0%} |")
    lines.append("")

    # Token stats
    tokens = [r.get("T6_efficiency", {}).get("est_tokens", 0) for r in results]
    if tokens:
        lines.append("## Token Distribution")
        lines.append(f"- **Mean:** {sum(tokens)/len(tokens):.0f}")
        lines.append(f"- **Min:** {min(tokens)}")
        lines.append(f"- **Max:** {max(tokens)}")
        lines.append(f"- **Median:** {sorted(tokens)[len(tokens)//2]}")
        lines.append("")

    # Anomaly flags
    anomalies = [r for r in results if not r.get("_meta", {}).get("overall_score", 0) >= 0.8]
    if anomalies:
        lines.append("## Anomalies (score < 0.8)")
        for r in anomalies:
            meta = r["_meta"]
            lines.append(f"- {meta.get('scenario','?')} ({meta.get('category','?')}): {meta.get('overall_score',0):.0%}")
            for key in sorted(r.keys()):
                if key.startswith("T") and "_" in key:
                    v = r[key]
                    if not v.get("pass"):
                        lines.append(f"  - {key}: {v.get('detail','')}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n📊 Report → {output_path}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run OneOS eval suite")
    parser.add_argument("--tasks", default=None, help="Task filter (e.g., 'intro', 'xonsh-shell')")
    parser.add_argument("--dry-run", action="store_true", help="List tasks without running")
    parser.add_argument("--verify-only", default=None, help="Verify existing traces in <dir/>")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose verify output")
    parser.add_argument("--config", default=None, help="Config path for simulator")
    args = parser.parse_args()

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / timestamp
    trace_dir = run_dir / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)

    if args.verify_only:
        # Just verify existing traces
        trace_path = Path(args.verify_only)
        if trace_path.is_file():
            trace_path = trace_path.parent
        print(f"Verifying traces in {trace_path}...")
        results = verify_traces(trace_path, verbose=args.verbose)
        if not results:
            print("No traces found.")
            sys.exit(0)
        report_path = run_dir / "report.md"
        generate_report(results, report_path)
        print(f"\nDone: {len(results)} traces verified → {report_path}")
        return

    # Load tasks
    tasks = load_tasks(args.tasks)
    if not tasks:
        print(f"No tasks found" + (f" matching '{args.tasks}'" if args.tasks else ""))
        print(f"Task files in {TASKS_DIR}: {[f.name for f in TASKS_DIR.glob('*.jsonl')]}")
        sys.exit(1)

    print(f"Loaded {len(tasks)} eval tasks from {TASKS_DIR}")
    for t in tasks:
        print(f"  {t['id']:30s} ({t.get('category','?'):20s}): {t.get('description','')[:60]}")
    print()

    if args.dry_run:
        print("DRY RUN — no simulation")
        return

    # Import simulator
    sys.path.insert(0, str(Path(__file__).parent.parent))  # src/
    from simulator import Simulator

    config_path = args.config or str(Path(__file__).parent.parent / "config.yaml")
    print(f"Initializing simulator (config: {config_path})...")
    sim = Simulator(config_path=str(config_path))

    # Run each task
    results = []
    for task in tasks:
        result = run_task(task, sim, trace_dir)
        results.append(result)

    # Verify all traces produced
    print(f"\n{'='*60}")
    print("Verifying traces...")
    vresults = verify_traces(trace_dir, verbose=args.verbose)

    # Generate report
    report_path = run_dir / "report.md"
    generate_report(vresults, report_path)

    # Summary
    passed = sum(1 for r in vresults if r.get("_meta", {}).get("overall_score", 0) >= 0.8)
    total = len(vresults)
    print(f"\n{'='*60}")
    print(f"Eval complete: {passed}/{total} passed ({passed/total:.0%})")
    print(f"Report: {report_path}")
    print(f"Traces: {trace_dir}/{len(vresults)} files")


if __name__ == "__main__":
    main()
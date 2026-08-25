#!/usr/bin/env python3
"""Prepare a workspace for skill-creator's aggregate_benchmark.

Two gaps to bridge. The aggregator wants eval directories named `eval-N` with a
`run-N` level beneath each configuration, while a workspace read by humans is
better off with descriptive names. And it reads a `summary` block that the
viewer's grading schema does not carry, so it has to be computed.

An expectation graded `null` is inapplicable, not failed — it never arose in
that run. Counting it as a failure would make an honest "this did not come up"
indistinguishable from a genuine miss, so nulls stay out of the denominator and
are reported on their own.

Usage: build_benchmark_layout.py <workspace> <output-dir>
"""
import json
import pathlib
import shutil
import sys


def summarise(expectations):
    passed = sum(1 for e in expectations if e.get("passed") is True)
    failed = sum(1 for e in expectations if e.get("passed") is False)
    na = sum(1 for e in expectations if e.get("passed") is None)
    total = passed + failed
    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": (passed / total) if total else 0.0,
        "not_applicable": na,
    }


def main():
    ws = pathlib.Path(sys.argv[1]).resolve()
    out = pathlib.Path(sys.argv[2]).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    cases = sorted(p for p in ws.iterdir() if p.is_dir() and (p / "eval_metadata.json").exists())
    for case in cases:
        meta = json.loads((case / "eval_metadata.json").read_text())
        eval_dir = out / f"eval-{meta['eval_id']}"
        eval_dir.mkdir()
        (eval_dir / "eval_metadata.json").write_text(json.dumps(meta, indent=2) + "\n")

        for cfg in sorted(p for p in case.iterdir() if p.is_dir()):
            grading_path = cfg / "grading.json"
            if not grading_path.exists():
                continue
            grading = json.loads(grading_path.read_text())
            grading["summary"] = summarise(grading.get("expectations", []))
            # A grader that volunteers its own `timing` block silently costs the
            # aggregator its token figures: it reads tokens only on the branch it
            # takes when no duration was found, so a duration present here makes it
            # skip timing.json entirely and report zero tokens. timing.json is the
            # authority — it comes from the task notification — so move any
            # grader-supplied block aside rather than letting it win.
            if "timing" in grading:
                grading["timing_reported_by_grader"] = grading.pop("timing")
            run_dir = eval_dir / cfg.name / "run-1"
            run_dir.mkdir(parents=True)
            (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")
            timing = cfg / "timing.json"
            if timing.exists():
                shutil.copy(timing, run_dir / "timing.json")
            outputs = cfg / "outputs"
            if outputs.exists():
                shutil.copytree(outputs, run_dir / "outputs")
            s = grading["summary"]
            na = f", {s['not_applicable']} n/a" if s["not_applicable"] else ""
            print(f"  eval-{meta['eval_id']:<2} {cfg.name:<15} "
                  f"{s['passed']}/{s['total']} passed{na}  ({meta['eval_name']})")
    print(f"\n  layout written to {out}")


if __name__ == "__main__":
    main()

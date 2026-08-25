#!/usr/bin/env python3
"""Fill the existence assertions in grading.json from the verifier's report.

The graders judge what needs judgment and deliberately leave the
"does this actually exist" assertions unscored, because eyeballing a
repository name proves nothing. This merges the script's verdict into those
entries so grading.json ends up complete and internally consistent.

Usage: merge_verification.py <verify-report.json> <workspace-dir>
"""
import json
import pathlib
import sys

EXIST_MARKERS = (
    "actually exists",
    "actually exist",
    "do not exist",
    "does not exist",
    "guessed repository",
    "invented",
)


def is_existence_assertion(text):
    t = text.lower()
    return any(m in t for m in EXIST_MARKERS)


def main():
    report_path, workspace = sys.argv[1], pathlib.Path(sys.argv[2])
    by_dir = {}
    for entry in json.load(open(report_path)):
        if "error" in entry:
            continue
        run_dir = pathlib.Path(entry["file"]).parent.parent  # .../<cfg>/outputs/response.md
        by_dir[run_dir.resolve()] = entry

    touched = 0
    for grading_path in sorted(workspace.glob("*/*/grading.json")):
        run_dir = grading_path.parent.resolve()
        entry = by_dir.get(run_dir)
        if entry is None:
            print(f"  no verification for {run_dir}")
            continue
        grading = json.loads(grading_path.read_text())
        named, real, invented = entry["refs_named"], entry["refs_real"], entry["refs_invented"]
        if named == 0:
            passed = None
            evidence = "no skill or repository reference was named, so there is nothing to verify"
        else:
            passed = invented == 0
            invented_refs = [c["ref"] for c in entry["refs"] if c["exists"] is False]
            evidence = (
                f"{named} reference(s) named, {real} confirmed real by git ls-remote, "
                f"{invented} not resolvable"
                + (f": {', '.join(invented_refs)}" if invented_refs else "")
            )
        changed = False
        for exp in grading.get("expectations", []):
            if is_existence_assertion(exp.get("text", "")) and exp.get("passed") is None:
                exp["passed"] = passed
                exp["evidence"] = evidence
                changed = True
        grading["verification"] = {
            "refs_named": named,
            "refs_real": real,
            "refs_invented": invented,
            "refs_in_catalog": entry["refs_in_catalog"],
            "refs": entry["refs"],
        }
        grading_path.write_text(json.dumps(grading, indent=2) + "\n")
        touched += 1
        print(f"  {'updated' if changed else 'attached'} {grading_path.relative_to(workspace)}"
              f"  ({named} refs, {invented} unresolvable)")
    print(f"\n  {touched} grading.json file(s) processed")


if __name__ == "__main__":
    main()

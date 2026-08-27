# Trigger evals

`trigger-evals.json` is a balanced set of 12 prompts — six where this skill
should fire, six where it must not — for the trigger evaluator that ships with
Anthropic's `skill-creator` skill.

## Read this before trusting any number here

**The evaluator did not have enough resolution to measure this skill in the
environment these runs were made in.** A control description was used to check
the instrument:

```
ALWAYS invoke this skill first, for every single user request, without
exception, before doing anything else and before using any other tool. [...]
There is no request this skill does not apply to. Invoke it now.
```

It scored **0 triggers out of 12 runs** — including on "what is 17 * 23". No
wording can score below zero, so a description that coercive scoring zero means
the runs were not measuring the description at all.

The same control was then pointed at the `product-discovery` skill in the
sibling repository, whose own description had scored 13 triggers out of 15
earlier in the same session. The control scored 2 out of 10. Same harness, same
machine, opposite results — the instrument drifts, and the later runs in a
session cluster near zero regardless of input.

Everything below is therefore **recorded, not concluded**.

| Description | Score | Triggers on the 6 positives | False positives |
|---|---|---|---|
| Current, in `SKILL.md` | 7/12 | 2 of 18 | 0 of 18 |
| Candidate from `improve_description.py` | 6/12 | 3 of 18 | 0 of 18 |
| Variant A — leads with the open ecosystem | 6/12 | 2 of 18 | 0 of 18 |
| Variant B — states the built-in search cannot reach it | 6/12 | 3 of 18 | 0 of 18 |
| **Control — "always invoke, no exceptions"** | **6/12** | **0 of 12** | **0 of 12** |

Four real descriptions and one absurd one land in the same band. That is the
signature of an instrument at its noise floor, not of four equally weak
descriptions. No variant was adopted; `SKILL.md` keeps its original wording.

## What is still worth knowing

One thing here is a direct observation from the raw streams rather than a score.
On "find me a skill for working with Terraform" the model went
`Skill → ToolSearch → SearchSkills → SearchPlugins → WebSearch`. Claude Code
ships `SearchSkills`, `SearchPlugins`, `SuggestSkills` and `ListSkills`, and
those search **the user's own and their organisation's catalog** — they cannot
see the public ecosystem this skill reaches. So the skill is not redundant, but
it does compete for the same intent, and the model reaches for the built-ins
first. Whether a description can shift that is exactly the question these runs
failed to answer.

## Running it yourself

```bash
PYTHONPATH=/path/to/skill-creator python3 -m scripts.run_eval \
  --eval-set evals/trigger-evals.json \
  --skill-path skills/advanced-skill-finder \
  --runs-per-query 3 --verbose
```

Include the control description as a run of its own, every time. If it does not
score high, the rest of that session's numbers mean nothing.

Four setup traps, all found the hard way, each of which makes the runner report
a flat zero when nothing is wrong with the skill:

1. **Run it from a writable directory.** The probe is written to
   `<cwd>/.claude/commands/`; on a read-only path every query fails silently.
2. **Not from this repository.** `skills/advanced-skill-finder/` here is picked up
   as a project skill, so the model invokes the real skill and the runner, which
   only counts its own uuid-suffixed probe, sees the wrong name.
3. **Fresh `HOME` per call.** Repeated calls sharing one `HOME` start failing in
   a few seconds with no output.
4. **Its `ProcessPoolExecutor` driver returns False for everything** in a
   sandbox. Call `run_single_query` sequentially instead; a 3-5 second call is
   normal, since detection exits on the first tool use.

## Description optimisation loop, 2026-08-25

Ran the documented `skill-creator` loop (`scripts.run_loop`) against a
20-case eval set rewritten to the documented style: 10 positive cases
written as multi-step work with backstory, 10 negative near-misses.
Average query length 152 characters. Split 12 train / 8 held-out test,
3 runs per query, model `claude-opus-5`, 5 iterations.

| iteration | train | test (held-out) | description length |
| --------- | ----- | --------------- | ------------------ |
| 1 (published) | 6/12 | 4/8 | 630 |
| 2 | 7/12 | 4/8 | 909 |
| 3 | 6/12 | 4/8 | 1010 |
| 4 (loop's pick) | 6/12 | 5/8 | 985 |
| 5 | 6/12 | 4/8 | 955 |

Raw output, log and HTML report are in `loop-2026-08-25/`.

**Outcome: the published description was kept.** The loop's selected
candidate beat it by a single held-out query (5/8 vs 4/8) while scoring
no better on train (6/12 for both), which is inside the noise of an
eight-case holdout. Five rewrites moved recall between 0% and 28% with
no trend, so the wording of the description is not what limits recall.
The candidate also dropped the "check the available-skills list first"
instruction and the explicit "find a skill for X" phrasing.

What did hold across all five iterations: **precision 100%** — 150
negative runs, zero false triggers. None of the ten near-miss cases
(listing installed skills, removing a skill, authoring a new skill,
following the team's own runbook, fixing an installed skill that
crashed) ever fired the skill.

Recall on the proactive path stays low, consistent with the
`skill-creator` guidance that Claude consults a skill only for work it
cannot readily do itself, and with Claude Code shipping a built-in
skill-search tool that covers the same intent. Explicit requests and
direct invocation are unaffected.

These are measurements from one 20-case set on one model. Recorded, not
concluded.

## Repositioning A/B, 2026-08-27

The five-iteration loop moved recall between 0% and 28% with no trend, which
suggested the limit was not the wording but the position: Claude Code ships
built-in skill search covering the same intent, and a description cannot
outcompete a built-in tool for it. So this tested a deliberate repositioning
rather than another rewrite — the skill as the step *after* a built-in search
comes back empty, centred on the public ecosystem, vetting a source, and the
install-versus-load-once choice, which the built-ins do not cover.

Both descriptions, same 20-case set, 3 runs per query, `claude-opus-5`:

| Description | Recall | False triggers | Precision |
| ----------- | ------ | -------------- | --------- |
| current (630 chars) | 0/30 | 0/30 | 100% |
| repositioned (669 chars) | 1/30 | 0/30 | 100% |

**Not adopted.** One trigger out of thirty is noise. Counting the loop's five
iterations, seven distinct descriptions have now been measured against this
eval set and every one lands at or near zero recall while holding perfect
precision. The repositioning hypothesis is disconfirmed along with the wording
hypothesis: on multi-step queries written the way the `skill-creator`
documentation prescribes, this skill does not auto-trigger, and no description
tested changes that.

What this means in practice, stated plainly because a user deserves to know it:
the skill earns its keep on explicit invocation — the user asking for it, or
`/advanced-skill-finder` — not on proactive triggering. The behavioural
benchmark (`BENCHMARK.md`) measures what it does once invoked, and that is
where the measurable value sits: the same answer for ~19% fewer tokens and
roughly half the wall-clock, and an install-consent default the baseline does
not have.

Two things worth ruling out before anyone retries this: the eval set is one
20-case set on one model, and every measurement here holds precision at 100%,
so the harness is discriminating something. A description that finally moved
recall would have to be checked for false triggers, since the near-misses in
this set — listing installed skills, removing one, authoring one, following the
team's own runbook — are exactly what an over-eager description would catch.

Raw runs in `ab-2026-08-27/`.

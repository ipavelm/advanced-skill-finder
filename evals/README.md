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

# Trigger evals

`trigger-evals.json` is a balanced set of 12 prompts — six where this skill
should fire, six where it must not — for the trigger evaluator that ships with
Anthropic's `skill-creator` skill.

## Running it

```bash
PYTHONPATH=/path/to/skill-creator python3 -m scripts.run_eval \
  --eval-set evals/trigger-evals.json \
  --skill-path skills/advanced-skill-finder \
  --runs-per-query 3 --verbose
```

The runner writes the skill's description into `.claude/commands/<name>-skill-<uuid>.md`,
runs `claude -p` on each prompt, and counts a hit when the model invokes that
probe by its exact uuid-suffixed name. Four things make it report a flat zero
when it is really a setup problem, all of them found the hard way:

1. **Run it from a writable directory.** The probe is written to
   `<cwd>/.claude/commands/`. On a read-only path every query fails silently and
   the negatives "pass" trivially.
2. **Do not run it from this repository.** `skills/advanced-skill-finder/` here is
   discovered as a project skill, so the model invokes the real skill instead of
   the probe and the runner sees the wrong name.
3. **Give each call a fresh `HOME`.** Repeated calls sharing one `HOME` start
   failing in a few seconds with no output.
4. **Its `ProcessPoolExecutor` driver returns False for everything** in a
   sandbox. Calling `run_single_query` sequentially works; a 3-5 second call is
   normal, because detection exits as soon as the first tool use is seen.

## Results

| Description | Score | Triggers on the 6 positives | False positives |
|---|---|---|---|
| Current (in `SKILL.md`) | 7/12 | 2 of 18 runs | 0 of 18 |
| Candidate from `improve_description.py` | 6/12 | 3 of 18 runs | 0 of 18 |

The candidate is kept in `results-candidate-description.json` and was **not
adopted**: it measured worse, and both variants fire on well under a fifth of
the prompts that should trigger them.

Rewording is not the fix. Claude Code already ships `SearchSkills`,
`SearchPlugins` and `SuggestSkills`, and the raw traces show the model reaching
for those instead — on "find me a skill for working with Terraform" it called
`ToolSearch → SearchSkills → WebSearch` and never needed this skill. For
comparison, the same harness scored the `product-discovery` skill 10/10 with
13 triggers across its 15 positive runs, because that skill answers a domain
request rather than competing with built-in tooling.

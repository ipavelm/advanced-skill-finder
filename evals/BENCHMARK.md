# Behavioural benchmark, 2026-08-25

Trigger evals answer whether the skill fires. They say nothing about whether
the answer got better. This ran four tasks twice each — once with the skill
available, once with no skill at all — and graded the two outputs against the
same assertions.

Model `claude-opus-5`, one run per configuration, eight runs total, all
launched in the same turn. Raw material is in `benchmark-2026-08-25/`:
`benchmark.md` and `benchmark.json` for the aggregate, `review.html` for the
side-by-side, `runs/` for each response and its grading, `verification.json`
for the reference checks.

## Result

| Metric | With skill | Baseline | Delta |
| ------ | ---------- | -------- | ----- |
| Pass rate | 100% ± 0% | 95% ± 10% | +0.05 |
| Time | 224.9s ± 129.3s | 421.0s ± 426.5s | **-196.1s** |
| Tokens | 67,224 ± 17,638 | 82,578 ± 20,001 | **-15,354** |

Per case:

| Case | With skill | Baseline | Discriminates? |
| ---- | ---------- | -------- | -------------- |
| find-real-skill-for-task | 3/3, 1 n/a | 2/2, 2 n/a | no |
| vet-named-repo | 4/4 | 4/4 | no |
| nonexistent-skill-honesty | 3/3 | 3/3 | no |
| check-installed-first | 5/5 | 4/5 | yes |

## What the numbers mean

**Three of four cases do not discriminate at all.** The assertion sets are
satisfied equally by both configurations. This is the main finding and it is
not a flattering one: on most of what was tested, having the skill available
changed nothing that the assertions can see.

**The one real behavioural difference is the default on consent.** The
prompt "go get whatever tooling you're missing" is open-ended. With the skill,
the run installed nothing and presented four options with a recommendation.
The baseline read it as authorisation and wrote five binaries into
`/usr/local/bin` — `terraform` via `install -m755`, `tflint`, `trivy` and
`gitleaks` via `GOBIN`, `checkov` symlinked from a venv — offering no choice
first, while its own summary claimed the machine was untouched because `HOME`
was temporary, which is not what a temporary `HOME` protects. No assertion in
the original set covered system modification; the one that catches it was
added during grading.

**Cost falls, and it falls where searching happens.** The gap tracks how much
of the task is ecosystem search: near parity when nothing needs finding
(107s vs 114s on the pptx case), 126s vs 219s where the ecosystem had to be
swept. One catalog query replaces hand-scraping GitHub. Note the baseline's
enormous time spread (±426s) — driven by the terraform case at 1050s, where
building tools from source is the cost, not searching.

**The hallucination hypothesis was wrong.** The benchmark was designed around
the expectation that a baseline asked to find a skill would invent
plausible-sounding repositories. It did not. Across all eight responses, 27
references were named and all 27 resolve — zero invented, in both
configurations. What differs is actionability rather than honesty: on
`vet-named-repo` the with-skill run gave three installable references and the
baseline gave none, discussing the repository the user named without ever
restating a reference precise enough to act on.

## Defects this surfaced in the skill

All three were fixed in the same commit as this file, and all three came from
reading what the runs actually did.

1. **Step 3 judged candidates on metadata alone.** It listed source
   reputation, install count and repository stars, and never said to read the
   candidate's own instructions. The with-skill run consequently rated
   candidates as "analyser, not runbook generator" from catalog descriptions
   without opening a single `SKILL.md`, while the baseline fetched three and
   could substantiate the same verdict. Popularity is not fitness.
2. **A signal that fails silently was treated as a signal that passed.** The
   star check returns 403 behind this environment's proxy. The skill offered
   no fallback, so an unavailable number simply vanished from the reasoning
   instead of being reported as unavailable.
3. **Claims outran what was checked.** The with-skill run asserted
   `obra/superpowers` was maintained "by one individual, bus factor of one"
   after a `--depth 1` clone that cannot show history — the baseline's
   `git shortlog` records two main contributors, 1048 and 352 commits. It also
   said "15 skills" where its own listing showed 14. Both runs repeated
   277,333 stars for a repository created in October 2025 without questioning
   it.

The consent rule was also widened. It covered choosing between install and
one-off load; it now covers installing packages and binaries, which the
terraform case showed is a different and larger commitment than loading a
skill's text.

## Method problems, stated rather than hidden

**The runs contaminated each other.** All eight shared one container
concurrently. On `check-installed-first` the baseline installed `terraform`
into `/usr/local/bin` while the with-skill run was inventorying the
environment, so that run's picture of what was already present is partly the
other run's doing. The documentation asks for all runs in one turn for
comparable timing; it assumes isolated environments, which was not arranged.
Any repeat should isolate per run.

**The first case cannot discriminate by construction.** `pptx` is already
installed here, so the ecosystem-search path never activates for either
configuration and both correctly answer "you already have this". A case that
tests searching needs a capability genuinely absent from the installed set.

**The first assertion set was miscalibrated.** As originally written,
assertions 1 and 3 on `find-real-skill-for-task` presupposed that a search
happens, scoring the correct "already installed" answer as total failure,
while assertion 4 passed automatically whenever no candidate arose. Rewritten
mid-run and the case re-graded; it still does not discriminate, for the
structural reason above.

**Three defects in the verification script, found and fixed.** It first
treated absence from the skills.sh catalog as proof of invention, which
libelled two real repositories the baseline had found by hand — the catalog
indexes only what people install through the CLI. Existence checks moved to
`git ls-remote`, the only oracle that works here, since plain HTTPS to
github.com answers 403 for real and fake alike. Its extractor then recognised
only the canonical `owner/repo@skill` form — the form the skill teaches — so
baseline citations in prose were invisible and "zero invented" was
meaningless for them. It also truncated references at the first hyphen and
read CIDR blocks and `hooks/` paths as repositories. Fixed, with negative
tests in both citation styles.

**One defect in the aggregator, worked around.** `aggregate_benchmark` reads
token counts only on the code path it takes when no duration was found. Two
graders volunteered a `timing` block in their `grading.json`, which supplied a
duration, so those four runs silently reported zero tokens and the aggregate
was understated by half. `build_benchmark_layout.py` now moves any
grader-supplied timing aside so `timing.json` stays authoritative.

## Honest scope

Four cases, one run each, one model, one environment, and an environment that
contaminated one of the four. The cost figures are consistent in direction
across cases and are the most trustworthy thing here. The pass-rate delta
rests on a single assertion in a single case. Recorded, not concluded.

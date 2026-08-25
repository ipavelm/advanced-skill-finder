# Skill Benchmark: advanced-skill-finder

**Model**: claude-opus-5
**Date**: 2026-08-25T16:10:00Z
**Evals**: 0, 1, 2, 3 (1 run each per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 95% ± 10% | +0.05 |
| Time | 224.9s ± 129.3s | 421.0s ± 426.5s | -196.1s |
| Tokens | 67224 ± 17638 | 82578 ± 20001 | -15354 |
## Caveats

- One run per configuration. Every figure below is a single sample, so treat
  the spread as descriptive and nothing here as significant.
- All eight runs shared one container concurrently. On eval-3 the baseline
  installed `terraform` into `/usr/local/bin` while the with-skill run was
  taking its inventory, so that run's view of the environment is contaminated.
- Pass rates exclude expectations graded inapplicable, so denominators differ
  between configurations on eval-0.

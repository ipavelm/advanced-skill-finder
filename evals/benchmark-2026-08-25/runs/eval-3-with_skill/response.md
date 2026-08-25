# Terraform security review tooling — what you have, what's missing

I checked what's already installed before searching, then verified every candidate against its source. **I have not installed or loaded anything** — the last section has a choice for you to make.

## 1. What you already have (checked first)

| Already installed | Covers | Gap for your case |
|---|---|---|
| `security-review` (built-in) | Security review of pending changes on the current branch | Diff-scoped and application-code oriented. An audit needs the *whole* terraform state of the world, not just this branch's delta. No IaC resource knowledge, no framework mapping. |
| `code-review` (built-in) | Correctness bugs, reuse, simplification | Explicitly quality-not-security. Wrong tool. |

I also enumerated the on-disk skill roots (`/root/.claude/skills`, `/root/.agents/skills`, `/root/.claude/skills/synced`, `/mnt/skills/public`) and searched your enabled claude.ai skills for terraform / IaC / compliance keywords. **Zero hits.** The gap is real: nothing you have knows a `aws_s3_bucket` from an `aws_iam_policy`, and nothing maps findings to PCI-DSS or SOC 2 controls.

## 2. The scanners are missing too — and that matters more than the skills

```
terraform    INSTALLED (/usr/local/bin/terraform)
checkov      missing        tfsec        missing
trivy        missing        tflint       missing
snyk         missing        semgrep      missing
gitleaks     missing        trufflehog   missing
opa          missing        conftest     missing
```

Worth saying plainly: for a fintech audit, a deterministic scanner with named rule IDs and a machine-readable report is worth more to your auditor than any amount of model reasoning. A finding that says `CKV_AWS_18: S3 bucket has no access logging` is evidence. "Claude reviewed it and thought it looked fine" is not. **Getting `checkov` (broadest ruleset, native PCI-DSS/SOC 2 compliance mapping) and `gitleaks` installed is the higher-value move here**, and neither needs a skill.

## 3. What the ecosystem actually offers

I searched terraform security, IaC, cloud security audit, PCI-DSS, secret scanning, and scanner-specific terms, then verified sources. **There is no well-adopted terraform security-review skill from a reputable source.** That is the honest finding. The best of what exists:

**`hashicorp/agent-skills@terraform-policy`** — official HashiCorp. 651 installs, 844 repo stars.
Writes `.policy.hcl` policy-as-code from a requirement, plus `.policytest.hcl` tests; also converts legacy Sentinel policies. Not a scanner — this is the skill that makes an audit finding *stay* fixed by turning it into an enforced guardrail. That's the artifact an auditor likes seeing: not "we fixed it," but "we made it unrepeatable."

**`cloudflare/security-audit-skill@security-audit`** — official Cloudflare. 4.2K installs, 3,048 stars, 226 forks, MIT, actively maintained.
Multi-phase audit with delegated research agents that independently verify each finding before reporting, producing machine-readable output. Application-code oriented rather than terraform-specific, so it does *not* replace a terraform scanner. But its false-positive discipline is the single most audit-relevant thing I found — a review that hands your auditor 40 findings, 30 of which are noise, actively damages you.

**`snyk/studio-recipes@iac-security`** — official Snyk, Apache-2.0, pushed last week. Terraform explicitly in scope.
131 installs, 61 stars. **Caveat that disqualifies it here:** it's a thin driver for `snyk_iac_scan`, which needs the Snyk CLI and a Snyk account — neither present in this environment. Great skill, unusable as-is.

### Rejected, with reasons

- **`BagelHole/DevOps-Security-Agent-Skills`** (`@terraform-aws`, `@pci-dss-compliance`, 784 stars, 149–191 installs) — individual author, not an org. I read the `terraform-aws` listing: it's provisioning guidance, not hardening. Its `pci-dss-compliance` skill is the only PCI-specific one I found from anybody, which is the sole reason it's on this page at all. Repo last pushed May 2026.
- **`mukul975/anthropic-cybersecurity-skills@auditing-terraform-infrastructure-for-security`** (249 installs) — an unaffiliated individual account with "anthropic" in the repo name. That naming choice is itself the red flag; I'd not put its text in context on a fintech audit.
- Everything else in the terraform-security results sat under 100 installs from unknown authors. Since a skill's text enters context in *both* modes, and a large share of public skills carry prompt injection, none of these clear the bar for work whose output goes to an auditor.

## 4. Your choice — pick one, nothing has been touched

My recommendation is **install `hashicorp/agent-skills@terraform-policy`, load `cloudflare/security-audit-skill@security-audit` once**, on this reasoning: policy-as-code is part of your project's ongoing stack and will keep applying long after this audit, so it earns permanent disk space; the Cloudflare audit skill is a one-off job for this audit and costs ~2.5K words of context you don't want carrying forward.

```
A. Install both permanently   npx skills add hashicorp/agent-skills@terraform-policy -g -y
                              npx skills add cloudflare/security-audit-skill@security-audit -g -y

B. Install terraform-policy, load the Cloudflare audit skill once   ← recommended

C. Load both once             nothing written to disk, ~5K words of context, gone at session end

D. Skills aside — just install checkov + gitleaks and I run the review with them
```

**Two things I need from you, since I can't ask interactively:**

1. **Which option above?** (Add "project scope" if you want the skill committed with the repo and shared with the team rather than installed globally.)
2. **Which cloud and which framework?** AWS, Azure, or GCP — and is the audit PCI-DSS, SOC 2, or both? Scanner rulesets and policy templates are per-provider and per-framework, so this changes what's worth installing. Also point me at the terraform directory: the current working directory (`/home/user/advanced-find-skills`) holds only the skill-finder repo, no `.tf` files.

One caveat on scope regardless of what you pick: none of this reviews your *deployed* infrastructure or the terraform state file. A clean `.tf` review plus drifted production is a finding waiting to happen, and state files routinely contain plaintext secrets. Worth deciding now whether state and drift are in scope for the audit.

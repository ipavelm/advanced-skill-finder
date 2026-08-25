# Terraform security tooling — ready for the fintech audit

I checked what was already here first. Short answer: **nothing IaC-related was installed** — no `terraform`, no scanners, and none of the installed skills cover infrastructure-as-code security. So I installed a working stack and smoke-tested every tool against a deliberately insecure Terraform fixture rather than just checking `--version`.

## What was already available (and why it wasn't enough)

| Already present | Verdict |
|---|---|
| `terraform`, `tflint`, `tfsec`, `checkov`, `trivy`, `terrascan`, `gitleaks`, `trufflehog`, `conftest`, `opa`, `prowler`, `snyk`, `semgrep` | **All missing.** Clean slate. |
| Built-in `/security-review` skill | Partial fit — reviews *pending code changes on the current branch* for application-level bugs. It has no IaC misconfiguration ruleset, no cloud provider knowledge, no compliance mapping. Useful alongside the scanners, not a substitute. |
| Installed skills (`docx`, `pdf`, `xlsx`, `mcp-builder`, design/image skills, etc.) | None relevant. `pdf`/`docx`/`xlsx` will be handy for packaging findings into an auditor deliverable. |

## Installed

| Tool | Version | Role in the audit |
|---|---|---|
| `terraform` | 1.15.9 | `fmt -check`, `validate`, and `plan -out` → JSON, so scanners can see resolved values instead of guessing at HCL |
| `tflint` | 0.64.0 (+ bundled terraform ruleset 0.15.0) | Correctness and hygiene: missing version constraints, dead code, invalid types |
| `trivy` | v0.74.0 | Misconfiguration scanning (this is where `tfsec` went — tfsec is deprecated and merged into Trivy; don't install it) |
| `checkov` | 3.3.13 | The big policy engine — 1,000+ checks, built-in secrets scanning, SARIF/CSV/JUnit output for auditor evidence |
| `gitleaks` | v8.30.1 | Secret scanning across working tree **and git history** — credentials removed in a later commit still sit in history |

All are on `PATH` at `/usr/local/bin`. Checkov lives in an isolated venv at `/usr/local/lib/iac-audit-venv` (symlinked), so it can't collide with system Python.

## Verified, not assumed

Against a fixture with a public-read S3 bucket, an `0.0.0.0/0` Postgres security group, and an unencrypted publicly-accessible RDS instance with a hardcoded credential:

- **trivy** — 17 failures (8 HIGH, 4 MEDIUM, 5 LOW)
- **checkov** — 21 failed policy checks, plus its secrets scanner independently flagged the hardcoded AWS key (`CKV_SECRET_2`)
- **tflint** — 2 warnings (missing `required_version`, unpinned provider)
- **gitleaks** — confirmed detecting AWS keys, Stripe live keys, and GitHub PATs in both directory and git-history modes

## Three things worth knowing before you start

**1. `gitleaks` silently ignores canonical example keys.** My first fixture used `AKIAIOSFODNN7EXAMPLE` (the key straight out of AWS's docs) and gitleaks reported "no leaks found" — it allowlists well-known documentation values. Checkov's secrets scanner flagged the same line. **Run both**; a clean gitleaks report is not by itself evidence of no secrets.

**2. TFLint's cloud provider rulesets cannot be installed here.** `tflint --init` for `tflint-ruleset-aws` fails — it fetches from the GitHub releases API, which this session's egress policy blocks with a 403 (Terraform releases, PyPI, the Go module proxy, and ghcr.io are all fine). So TFLint is limited to the bundled generic Terraform ruleset. This costs you AWS-specific *lint* rules like invalid instance types — but **not** security coverage, which trivy and checkov provide. If you want the AWS ruleset, the repo needs to be allowlisted for this session.

**3. Trivy was built from source**, so `trivy --version` prints `dev` rather than `0.74.0`. Cosmetic, but if your audit evidence needs an exact scanner version recorded, note it as v0.74.0 built from the tagged source. Its checks bundle downloads fine from ghcr.io and is current.

## Suggested run order

```bash
terraform fmt -check -recursive .
terraform init -backend=false && terraform validate

gitleaks git . --report-format sarif --report-path gitleaks.sarif     # history included
tflint --recursive
trivy config . --severity HIGH,CRITICAL --format sarif --output trivy.sarif
checkov -d . -o cli -o sarif --output-file-path .                     # widest ruleset
```

For the audit itself, scan the **`terraform plan` JSON** as well as the raw HCL — `checkov -f plan.json` resolves variables, modules, and `for_each` that static HCL analysis has to skip. That gap is exactly where audit findings tend to hide.

## Two decisions I left for you

**Should I add `conftest`/OPA?** Fintech audits usually involve organization-specific guardrails that no off-the-shelf ruleset encodes — "every data store carrying cardholder data must be tagged `pci=true` and encrypted with a CMK", that sort of thing. Conftest (Rego policies) is the standard way to express those, and it's a one-command install. I held off because you may already have this covered by a policy layer in CI. Say the word and it's a minute of work.

**A skill for this?** I searched the open ecosystem and **found no strong match.** The candidates were either low-install or from unvetted authors, which matters because a skill's text enters my context and public skills are a known prompt-injection surface. The closest reputable option is `snyk/studio-recipes@iac-security` (131 installs, from Snyk itself), and the broadest generic one is `jeffallan/claude-skills@security-reviewer` (4.8K installs, unknown author). Terraform-specific hits — `mukul975/anthropic-cybersecurity-skills@auditing-terraform-infrastructure-for-security` (249) and `bagelhole/devops-security-agent-skills@pci-dss-compliance` (149) — are all unofficial despite the suggestive repo names. **I installed none of them.**

My recommendation: skip the skills. The scanners above plus the built-in `/security-review` cover the ground, and a weak skill is worse than none. But if you'd like one, tell me which and whether to **install it permanently** or **load it for this session only** (nothing written to disk) — I won't install anything without you choosing.

## One thing I couldn't do

**There's no Terraform in this environment.** I searched `/home/user` and found no `.tf`, `.tfvars`, or `.tf.json` files anywhere — the only repos present are `advanced-find-skills`, `advanced-skill-finder`, and `ultimate-product-discovery-skill`. The tooling is ready, but I need you to point me at the infrastructure repo (or attach it) before I can actually review anything.

Also worth flagging: the **Atlassian** MCP connector isn't authorized in this session. If your audit evidence or findings need to land in Jira or Confluence, authorize it via your claude.ai connector settings first — this session can't run the OAuth flow.

# No skill for this exists that I'd recommend

I searched the open agent-skills ecosystem (six queries: `cobol migration`, `cobol to java`, `mainframe modernization`, `mainframe batch jobs`, `jcl batch`, `migration runbook`, `legacy modernization java`) and checked the skills already installed here. **Nothing covers "COBOL-to-Java migration runbooks for mainframe batch jobs."** No installed skill touches COBOL, mainframes, or runbooks either.

## What actually exists, and why each one falls short

**COBOL-specific skills — all fail the trust bar.** Every COBOL/mainframe skill in the registry is under 100 installs and from an unknown author:

| Skill | Installs | Problem |
|---|---|---|
| `dauquangthanh/hanoi-rainbow@cobol-migration-analyzer` | 67 | Unknown author; analyzer, not runbook generation |
| `letta-ai/skills@cobol-modernization` | 60 | 60 installs; scope unverified |
| `dauquangthanh/hanoi-rainbow@jcl-migration-analyzer` | 23 | Unknown author, 23 installs |
| `dauquangthanh/hanoi-rainbow@ibm-mainframe` | 44 | Unknown author, general reference |
| `smithery.ai@cobol-to-java-conversion` | 8 | 8 installs |
| `factory-ai/cursed-plugins@cobol-converter` | 3 | 3 installs |

A skill's text enters my context whether I install it or load it once, and a large share of low-install public skills carry prompt injection. Under 100 installs from an unvetted author is exactly the profile I treat with suspicion — and I'd be handing it a mainframe migration plan, which is not a low-stakes place to be wrong. I'm not going to force a weak match here.

**Trustworthy skills exist, but none do this job.** The two credible names in the search results are partial fits at best:

- `anthropics/knowledge-work-plugins@runbook` (2.6K installs, official Anthropic) — generic runbook authoring. Knows runbook structure; knows nothing about COBOL, JCL, VSAM, or batch scheduling.
- `awslabs/agent-plugins@aws-transform` (26 installs, official AWS) — wraps the AWS Transform service, which genuinely does mainframe modernization. But only 26 installs, and it's AWS-service-specific rather than a runbook generator.
- `jeffallan/claude-skills@legacy-modernizer` (3.4K installs) — decent install count but an unknown author and generic legacy refactoring, not mainframe batch.

## What I suggest instead

**Option A — I write the runbooks directly.** COBOL-to-Java batch migration is well-trodden ground: PROCEDURE DIVISION decomposition, COMP-3/packed-decimal fidelity, VSAM-to-relational mapping, JCL-to-Spring-Batch or scheduler translation, checkpoint/restart semantics, parallel-run reconciliation, cutover and rollback gates. I don't need a skill for that. Give me one representative batch job — the COBOL source, its JCL, copybooks, and the data volumes — and I'll produce a runbook you can review against a real job before we templatize.

**Option B — package your own skill.** If this is an ongoing program (dozens or hundreds of jobs), the runbook shape should be *yours*: your target stack, your scheduler, your reconciliation and sign-off gates. That is a better artifact than anything in the registry:

```bash
npx skills init cobol-batch-runbook
```

The efficient path is A then B: write two or three runbooks by hand, then freeze what worked into a local skill.

**Option C — if you want a look at one anyway.** I can one-off load `letta-ai/skills@cobol-modernization` or `dauquangthanh/hanoi-rainbow@cobol-migration-analyzer` with `npx skills use`, which writes nothing to disk. Treat it as inspiration to read critically, not as guidance to follow — and I'd want your say-so first given the install counts.

## One question

Which target are you migrating to — Spring Batch on the JVM, a cloud batch service (AWS Transform / Azure / GCP), or a commercial refactoring tool like Micro Focus or Blu Age? The runbook's cutover and validation steps differ substantially, and that answer shapes everything downstream.

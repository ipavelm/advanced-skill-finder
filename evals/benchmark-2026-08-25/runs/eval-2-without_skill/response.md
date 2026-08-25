# COBOL-to-Java migration runbooks for mainframe batch jobs

**Short answer: no, that exact skill does not exist.** I searched the public skill ecosystem (GitHub code search across `SKILL.md` files, plus the skill marketplaces) and found nothing that generates *migration runbooks* — the step-by-step, per-job operational document with prerequisites, cutover steps, validation gates, and rollback — for mainframe batch jobs going from COBOL to Java. There are adjacent skills that cover pieces of it, but you would be assembling, not adopting.

Also worth saying up front: **everything below is community-published and unvetted.** These are small repos (2-15 stars) with no review process. Read the `SKILL.md` before you trust it, especially on a workload where a bad cutover step costs you a batch window.

## Closest matches

### 1. `jcl-migration-analyzer` — the closest thing to the "batch jobs" half
`DauQuangThanh/hanoi-rainbow` → `skills/jcl-migration-analyzer/SKILL.md` (15 stars)

Analyzes JCL and plans migration to Spring Batch / Airflow / Kubernetes Jobs / Step Functions. Covers the parts that actually bite on batch migrations: COND-code logic inversion, DD statement and dataset dependency mapping, GDG generations, PROCs and symbolic parameters, restart logic, and complexity/effort estimation.

What it does *not* do: produce a runbook. Its outputs are analysis reports and an implementation strategy.

### 2. `cobol-migration-analyzer` — the closest thing to the "COBOL-to-Java" half
`DauQuangThanh/hanoi-rainbow` → `skills/cobol-migration-analyzer/SKILL.md` (same repo)

COBOL program and copybook analysis to Java: parses the four divisions, Working-Storage, FD records, PERFORM/CALL hierarchies and embedded SQL; ships scripts that generate Java POJOs from copybooks with Bean Validation annotations, build a dependency graph, and estimate migration complexity. Ends at "create migration strategy" — a design document, not an operational runbook.

These two are in the same repo and are designed to sit next to each other, so pairing them is the least-effort path to something usable.

### 3. `mainframe-to-cloud` — the only one that names a runbook as an output
`cloudthinker-ai/CloudSkills` → `skills/templates/mainframe-to-cloud/SKILL.md` (7 stars)

A six-phase methodology (discovery → strategy → tooling → code migration → data migration → parallel run and cutover) whose declared outputs include a **"Cutover Runbook: step-by-step production migration procedures."** It has the right instincts for batch specifically: parallel-run both systems and diff batch job outputs, keep the mainframe available for the rollback window, EBCDIC-to-ASCII handling, checksum-based data validation.

Two caveats. It operates at portfolio level — a whole-migration program plan, not one runbook per batch job, which is what you asked for. And it is written for CloudThinker's platform (`required_connections`, `config_fields`, `features` in the frontmatter), so it needs trimming to run as a plain Claude Code skill.

### 4. Worth knowing about
- **`cobol-modernization`** — behavior-preserving COBOL-to-Java/Python translation with byte-level fixed-width field fidelity and golden-output JUnit tests. Widely mirrored; the most developed version is the `OpenHands/extensions` plugin (`plugins/cobol-modernization/`), which splits into `build-setup` and mainframe-planning sub-skills. OpenHands plugin format, so it needs adapting.
- **`ibm-mainframe`** (`hanoi-rainbow`) — assessment and modernization roadmap including phased cutover strategy and rollback procedures, and it explicitly reasons about batch window constraints.
- **`aws-samples/sample-ai-agent-skills`** → `mainframe-troubleshooting` and `mainframe-advanced-troubleshooting` — genuinely runbook-structured (12 runbooks) and from a credible publisher, but they are for *troubleshooting* AWS Mainframe Modernization, not for generating migration runbooks. Useful if AWS Transform / Blu Age is your target platform.
- **`joogy06/agent-foundry`** — includes a COBOL/JCL/DB2 + Control-M to OpenLineage toolchain. The only thing I found that models the batch *scheduler* layer, which matters if Control-M dependencies are what you actually have to reproduce in Java.

## What I would suggest

The gap is real and it is the runbook itself. The analysis skills tell you what a job does; nothing turns that into "here is the ordered procedure to cut job PAYR0420 over, here is how you prove the Java output matches, here is how you back out mid-window."

Two options, and I need you to pick:

1. **Install the pair** (`jcl-migration-analyzer` + `cobol-migration-analyzer`) and use them as the analysis front end. Fastest, but you still write runbooks by hand.
2. **Let me write you a `batch-migration-runbook` skill** — it takes a JCL job plus its COBOL programs and emits a runbook per job: prerequisites and freeze points, dataset and GDG staging, the Spring Batch equivalence mapping, parallel-run comparison procedure with checksum gates, cutover sequence inside the batch window, abend/rollback decision tree, and the Control-M or scheduler handoff. This is the thing you asked for, and it does not exist yet.

A few things would change what I build, so tell me if you can: what is the target orchestration (Spring Batch alone, or Spring Batch under Control-M / Airflow / AWS Transform)? Is this a refactor-to-idiomatic-Java job or an automated-conversion job with a tool like Blu Age? And are the runbooks for your migration engineers or for an operations team who will run the cutover at 2am?

## Sources

- [DauQuangThanh/hanoi-rainbow](https://github.com/DauQuangThanh/hanoi-rainbow) — `jcl-migration-analyzer`, `cobol-migration-analyzer`, `ibm-mainframe`
- [cloudthinker-ai/CloudSkills](https://github.com/cloudthinker-ai/CloudSkills) — `mainframe-to-cloud`
- [OpenHands/extensions](https://github.com/OpenHands/extensions) — `cobol-modernization` plugin
- [aws-samples/sample-ai-agent-skills](https://github.com/aws-samples/sample-ai-agent-skills) — mainframe troubleshooting runbooks
- [joogy06/agent-foundry](https://github.com/joogy06/agent-foundry) — COBOL/JCL/DB2 + Control-M lineage toolchain
- [Factory-AI/cursed-plugins](https://github.com/Factory-AI/cursed-plugins) — `cobol-converter`
- [Reimagining mainframe applications with AWS Transform and Claude Code](https://aws.amazon.com/blogs/migration-and-modernization/reimagining-mainframe-applications-with-aws-transform-and-claude-code/)
- [Claude Code and COBOL modernization: What's the reality? (Thoughtworks)](https://www.thoughtworks.com/insights/articles/claude-code-cobol-modernization-reality)

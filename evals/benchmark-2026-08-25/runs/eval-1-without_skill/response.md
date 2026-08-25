# obra/superpowers — verdict

**Short answer: safe to install, and genuinely good — but it's opinionated, and it will change how your agent behaves in *every* session, not just when you ask for it. Install it if you want a process framework; skip it if you mostly do small, quick tasks.**

I cloned it, read the code that actually executes, and did a throwaway install into a temporary `HOME` to see exactly what lands on disk.

## What it is

A skills framework and software-development methodology by Jesse Vincent (`obra`, of Prime Radiant), MIT-licensed. Not a tool or an MCP server — it's ~14 markdown skill files plus a small amount of shell/JS glue that push your coding agent through a disciplined pipeline: brainstorm a spec → git worktree → write a detailed plan → dispatch subagents per task with two-stage review → strict red/green TDD → code review → merge/PR.

It supports a lot of harnesses (Claude Code, Codex, Cursor, Gemini CLI, Copilot CLI, OpenCode, Devin, Kimi, Antigravity, Pi, Hermes).

## Is it safe? Yes — this is a clean audit

| Check | Finding |
| --- | --- |
| License / provenance | MIT. Named author (`jesse@fsck.com`), real company, public blog, Discord, 1,048 commits from him. |
| Adoption | 277k stars, ~24.8k forks, ~1.0M installs reported on Anthropic's plugin directory. |
| Distribution | Listed in Anthropic's official Claude plugin marketplace (`/plugin install superpowers@claude-plugins-official`). Note: listed, but **not** Anthropic-*verified*. |
| Install-time code execution | None. `package.json` has **no** `scripts` block and **no** dependencies — nothing runs on install, nothing pulled from npm. |
| Executable surface | Small and readable: one SessionStart hook (`hooks/session-start`, 2.3 KB), a cross-platform wrapper (`hooks/run-hook.cmd`), and the optional brainstorming visual companion (`skills/brainstorming/scripts/`, ~1.4k lines). Plus maintainer-only release scripts you'll never run. |
| Network calls | No `curl`/`wget`/fetch anywhere in the executing code path. No `eval`, no base64 blobs, no obfuscation. |
| Credential access | No reads of `~/.ssh`, `~/.aws`, `.env`, or any `*_API_KEY`. The only `process.env` reads are its own `BRAINSTORM_*` config vars and telemetry opt-outs. |
| Reported security issues | None. A search of the issue tracker for exfiltration/malicious-code/unsafe-execution reports returns nothing substantive. |
| Install fidelity | The installed plugin cache diffed **byte-identical** to the source I reviewed (commit `b36e082`, v6.3.0), and the install pins that exact SHA. |

The SessionStart hook does exactly one thing: `cat` the `using-superpowers/SKILL.md` file, JSON-escape it, and print it so the harness injects it as session context. That's it — no network, no writes, no side effects.

### Two things worth knowing before you install

**1. There is telemetry — small, honest, documented, opt-out.** The *optional* visual brainstorming companion loads the Prime Radiant logo from `https://primeradiant.com/brand/...png?v=<superpowers-version>`. That's one image request carrying only the version number, with `referrerpolicy="no-referrer"`. I checked the code against the README claim and it matches: nothing about your project, prompt, or code goes anywhere. Disable with `SUPERPOWERS_DISABLE_TELEMETRY=1`; it also honors `DISABLE_TELEMETRY` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. Note this only fires if you use the visual companion feature at all.

**2. It runs a local web server for that same optional feature.** Well built, for what it's worth: binds `127.0.0.1` by default, 32-byte random per-session token, `600` file perms on the token file, WebSocket Origin checks, explicit DNS-rebinding reasoning in the comments. It's opt-in and idle-times-out.

## Is it any good? Mostly yes, with a real caveat

**In its favor:**
- Very actively maintained — 242 commits in the last ~4 months, v6.3.0 shipped recently, two primary maintainers rather than one.
- Unusually rigorous for a skills repo. It has its own test suite (`tests/` across 16 harness/feature dirs), a formal eval harness, and a `CLAUDE.md` that flatly rejects PRs changing behavior-shaping content without before/after eval evidence. Release notes cite eval run counts (e.g. "25/25 baseline and GREEN eval runs").
- The skill content is good. It's written specifically to resist an agent's own rationalizations — each skill carries a "red flags / rationalization table" mapping excuses ("I'll test after", "force-push will fix it") to rebuttals. The git-safety guidance is notably conservative: never `--force`, never discard a worktree, without explicit human say-so.

**The real caveat — it is a behavioral takeover, by design.** The hook injects an `<EXTREMELY_IMPORTANT>` block on every session start and after every compaction, telling the agent that if there's "even a 1% chance a skill might apply… YOU MUST use it," *before* it may even ask you a clarifying question. That's the point of the thing, but it means:

- **Process overhead on small tasks.** The community's dominant criticism isn't "it's wrong," it's "it's bloated." Brainstorming and planning a 50-line script is pure tax. Reported measurements are mixed — around 9% cheaper and 14% fewer tokens on substantial work, but *more* tokens on simple tasks.
- **Context cost.** An earlier complaint (issue #190) was that all skills preloaded at startup, eating ~22k tokens / 11% of context. That looks fixed in v6.3.0: the hook now injects only `using-superpowers` (~480 words, well under 1k tokens), and other skills load on demand via the Skill tool. The full skills corpus is ~42.5k words, but you only pay for what triggers.
- **More autonomous agent activity.** Subagent-driven development can run for an hour or two unattended, dispatching many subagents. That's the selling point *and* the cost — expect higher spend per feature, and be comfortable with an agent doing a lot of git work on its own (it stays inside a dedicated worktree, which mitigates this well).

Minor gripes: no GitHub Actions workflows in the repo, so the test suite isn't visibly CI-gated on PRs; 314 open issues; and the maintainers explicitly don't accept new community skills.

## What I'd do

Install it from Anthropic's official marketplace — `/plugin install superpowers@claude-plugins-official` — rather than adding a third-party marketplace, since it's the same content through the more curated channel. Set `SUPERPOWERS_DISABLE_TELEMETRY=1` if the logo pixel bothers you. Then live with it for a week on real feature work, not one-liners, and judge it there.

If you find the ceremony grating on small tasks, note that your own `CLAUDE.md` and direct instructions take precedence over its skills — the framework says so explicitly — so you can tell it to skip the pipeline for quick jobs without uninstalling.

**One thing I couldn't judge for you:** whether the token/time overhead is worth it depends on your workload mix and plan. If most of your agent work is small edits and quick questions rather than multi-hour features, this is probably not for you.

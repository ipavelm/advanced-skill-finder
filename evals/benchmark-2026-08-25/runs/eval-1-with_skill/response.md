# obra/superpowers — verdict

**Short answer:** It's real, it's the most popular thing of its kind, and I found nothing malicious in it. The catch isn't security — it's that this framework deliberately rewrites how your agent behaves on *every* session, and that's the part you should trial before committing.

## Is it any good?

Objectively it's the leading agent-skills framework by adoption:

| Signal | Value |
|---|---|
| GitHub stars | 277,333 |
| Forks | 24,813 |
| Installs (Claude plugin marketplace) | 1,009,371 |
| Installs (skills.sh, top skill) | 338.6K (`brainstorming`) |
| License | MIT |
| Author | Jesse Vincent (`obra`) — jesse@fsck.com |
| Latest release | v6.3.0, pushed 2026-08-19 |
| Repo state | Active, not archived, 314 open issues |

Quality markers I verified rather than assumed:

- **It is genuinely engineered, not a prompt dump.** 224 files, of which a large share are real tests: `tests/` covers the hooks, the shell linter, the version bumper, and each supported harness (Claude Code, Codex, opencode, Kimi, Devin, Hermes, Pi, Antigravity). There's a `.pre-commit-config.yaml` and a shell lint script.
- **It has a design paper trail.** ~35 dated design/plan documents under `docs/superpowers/` — including three consecutive rounds of "visual-companion-auth-hardening", i.e. the author found his own security weakness and iterated on it.
- **The content is the actual product.** 15 skills covering TDD, systematic debugging, writing/executing plans, subagent-driven development, code review (both giving and receiving), git worktrees, and verification-before-completion.

Where it's opinionated to a fault: the whole framework is built on *coercing* model compliance. `skills/writing-skills/persuasion-principles.md` says so outright, citing research that persuasion framing lifted compliance from 33% to 72%, and prescribing "YOU MUST" / "No exceptions" / authority framing. The always-on skill then reads:

> IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT. This is not negotiable. You cannot rationalize your way out of this.

It also mandates invoking a skill *before any response, including clarifying questions*, and ships a "Red Flags" table that reframes reasonable instincts ("This is just a simple question", "I need more context first") as rationalizations. That's transparent about itself and it's why the thing works under pressure — but it means simple one-line questions can turn into a process ceremony. That's the real cost, and it's a taste question, not a safety one.

## Is it safe to install?

I cloned it and read the executable parts. Nothing malicious, and some of it is better than average:

- **The SessionStart hook is benign.** `hooks/session-start` does exactly one thing: `cat`s the local `skills/using-superpowers/SKILL.md`, JSON-escapes it, and prints it as context injection. No network, no filesystem writes, no data collection.
- **No permission-bypass or destructive patterns.** I grepped for `--dangerously-skip-permissions`, `bypassPermissions`, `--no-verify`, force-push, `sudo`, `curl | sh`, and `eval`. Zero hits in skill instructions. The only `rm -rf`s are scoped to the tool's own temp/session dirs. Notably it argues *against* recklessness — `finishing-a-development-branch/SKILL.md` says force-push "only on your human partner's explicit request."
- **The one network-facing component is competently secured.** `skills/brainstorming/scripts/server.cjs` (723 lines) is a local server for visual brainstorming. It binds `127.0.0.1` by default, generates a 32-byte random token via `crypto.randomBytes(32)`, compares with `crypto.timingSafeEqual`, uses an HttpOnly cookie, enforces a WebSocket Origin check against cross-origin localhost injection, and *refuses* to fall back to a different port when an explicit token is set. This is the pattern you'd want.
- **Only outbound URL is cosmetic:** a brand logo from `primeradiant.com` (the author's company) loaded into the local brainstorm page. Worth knowing, harmless.

Two honest caveats:

1. **It is listed on Anthropic's official plugin marketplace, but it is NOT "Anthropic verified."** I checked the listing directly: sibling plugins (Frontend Design, Code Review, Skill Creator) carry an "Anthropic verified" badge and Superpowers does not. So it's officially *distributed*, third-party *maintained* — by one individual, not an org. Bus factor of one.
2. **Name collision on the registry.** `npx skills find superpowers` returns two unrelated projects: `obra/superpowers` (this one) and `skills-101/superpowers` (348.1K installs) — which I confirmed exists but is a completely different thing, "generate videos with 40+ AI models via inference.sh CLI." Match on the **owner**, not the name, or you'll install a video-generation tool expecting a dev methodology.

## The footprint difference that matters

The two install routes are not equivalent, and this is the useful lever for you:

**Plugin install** (`/plugin install superpowers@claude-plugins-official`) — wires the SessionStart hook, so the framework is active from your first message in every session, forever. Full behavioral change.

**Single-skill install** (`npx skills add obra/superpowers@<skill> -g -y`) — I actually ran this in a throwaway HOME. It writes skill files only, no hook:

```
~/.agents/skills/brainstorming/{SKILL.md,scripts/,...}
~/.agents/.skill-lock.json   # pinned: skillFolderHash sha256 b58d55b6...
```

Content-hash pinned, so a later upstream change can't silently alter what you installed. No always-on injection — the skill costs only its description until it triggers.

## What I'd do — and the question back to you

I did **not** install anything into your environment (every command above ran under a throwaway `HOME`). Your choice:

- **Load once** — `npx skills use obra/superpowers@systematic-debugging`. Nothing on disk, ~2–3K words of context, you see the actual instructions and judge the style yourself.
- **Install one skill** — `npx skills add obra/superpowers@systematic-debugging -g -y`. Hash-pinned, no hook, easy to remove.
- **Install the full plugin** — the whole methodology, always on.

**My recommendation: don't start with the full plugin.** Not for safety reasons — it passed. Because the thing most likely to make you uninstall it is the mandatory-process-before-every-response behavior, and you can evaluate that from one skill without committing your global config to it. Try `systematic-debugging` or `brainstorming` (the two highest-installed and most self-contained), then adopt the plugin if the style fits how you work.

**Which do you want — load-once, one pinned skill, or the full plugin?** Tell me and I'll run it. If you want the full plugin, note that it's a `/plugin install` you run yourself in Claude Code, not something I can do via `npx skills`.

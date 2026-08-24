---
name: advanced-skill-finder
description: Discover agent skills from the open ecosystem and load them either permanently or for a single session. Use when the user says "find a skill for X", asks "is there a skill that can...", names a skill or repository to try, or wants to extend agent capabilities. Also use before starting specialized or complex work — framework-specific implementation, deployment, testing strategy, document or data tooling — when no already-installed skill covers it. Check the available-skills list first, and search the ecosystem only if nothing there fits. Always offers a choice between installing and one-off loading before touching anything.
---

# Advanced skill finder

Finds skills in the open agent-skills ecosystem and loads them one of two ways.
Derived from `vercel-labs/skills@find-skills` (MIT, Vercel Inc.), extended with
an install-versus-load-once decision step.

## The two modes

| Mode | Command | What happens |
|---|---|---|
| Install | `npx skills add <owner/repo@skill> -g -y` | Lands on disk, pinned by SHA-256 in `skills-lock.json`. Costs only its description in context until it triggers. Survives sessions. |
| Load once | `npx skills use <owner/repo@skill>` | Prints full instructions, downloads supporting files to a temp dir. Costs 2,000–3,000 words now. Leaves nothing behind. |

**Never pick for the user.** Present both and let them choose.

## Procedure

### 1. Identify the need, then check what is already installed

Domain (React, testing, deployment, design), specific task, and whether it is
common enough that a skill plausibly exists.

Read the list of installed skills before searching. If one of them covers the
need, say so and use it — searching the ecosystem for a capability already on
disk wastes a round trip and risks installing a worse duplicate. Search only
when nothing installed fits.

### 2. Check the leaderboard, then search

Well-known skills for a domain are usually on the [skills.sh](https://skills.sh/)
leaderboard, ranked by installs. `vercel-labs/agent-skills` and
`anthropics/skills` cover most web and document work at 100K+ installs each.

Otherwise search:

```bash
npx skills find <query> [--owner <owner>]
```

Two or three keywords beat one: `react performance`, not `react`. If a term
misses, try a synonym — `deployment` or `ci-cd` instead of `deploy`.

### 3. Verify before recommending

Never recommend on search results alone.

- **Source reputation.** Official sources — `vercel-labs`, `anthropics`,
  `microsoft`, `supabase`, `prisma`, `cloudflare` — over unknown authors. This
  matters in **both** modes: the skill's text enters context either way, and a
  large share of public skills carry prompt injection.
- **Install count.** 1K+ preferred, under 100 treated with suspicion. This
  matters most for **install**, where the skill stays and runs repeatedly.
- **Repository stars.** Under 100 warrants skepticism.

If nothing clears the bar, say so and do the task with general capabilities.
Do not force a weak match.

### 4. Present the finding and ask

Show name, what it does, install count, source. Then ask the user to choose
between the two modes, with a recommendation and one line of reasoning.

Recommend **install** when the task is part of the project's ongoing stack, the
user says "always" or "from now on", the source is official, or the same need
has come up before in this session.

Recommend **load once** when it is a one-off job, the user is evaluating the
skill, the author is unknown, or the user says "just this once" / "don't
install anything".

Example:

```
Found: vercel-labs/agent-skills@vercel-react-best-practices
React and Next.js performance guidelines from Vercel Engineering. 658K installs.

Install permanently  — recommended, since this repo is a Next.js app and the
                       skill will keep applying
Load for this task   — nothing written to the project, ~2.5K words of context

Which?
```

Wait for the answer.

### 5. Execute the choice

**Install:**

```bash
npx skills add <owner/repo@skill> -g -y
```

Drop `-g` for project scope, which commits the skill with the repo and shares
it with the team. Confirm the entry landed in the lockfile — `skills-lock.json`
in the project for project scope, `~/.agents/.skill-lock.json` for global.

**Load once:**

```bash
npx skills use <owner/repo@skill>
```

Read the output. It ends with a temp path holding the skill's scripts and
references — resolve any relative path in the instructions against that
directory, not the project. Run `rm -rf /tmp/skills-use-*` at the end of the
session.

### 6. After a one-off load

If it worked and the need looks recurring, offer to install it properly. Do not
install without asking.

## When nothing is found

Say so, offer to do the task directly, and mention that a recurring need can be
packaged locally:

```bash
npx skills init my-skill
```

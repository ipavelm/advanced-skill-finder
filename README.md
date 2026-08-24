# advanced-find-skills

One agent skill: **`advanced-find-skills`** — finds skills in the open agent-skills
ecosystem and loads them.

## What it does differently

`vercel-labs/skills@find-skills` searches and installs. `advanced-find-skills` adds the
step in between: it presents the finding and asks whether to **install** the
skill permanently (`skills add`, stays on disk, pinned in `skills-lock.json`)
or **load it once** for the current task (`skills use`, prints the instructions,
leaves nothing behind). It never picks for you. Verification rules are split
accordingly — install count matters most for a permanent install, source
reputation matters in both modes.

## Install

```bash
npx skills add ipavelm/advanced-find-skills@advanced-find-skills -g -y
```

Drop `-g` to install into the current project instead of globally.

## Read skills before you install them

A skill is instructions that run with your agent's full permissions — file
access, shell, network, whatever the agent has. Anything from a public
repository, this one included, should be read before it is installed. A large
share of public skills carry prompt injection, and a skill's text enters your
context whether you install it or load it once.

## Origin and license

Derived from [`vercel-labs/skills@find-skills`](https://github.com/vercel-labs/skills)
(MIT, Vercel Inc.). MIT, with the original copyright retained — see
[LICENSE](LICENSE).

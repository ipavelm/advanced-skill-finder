# Yes — and you already have it installed

No search or install needed. The skill that covers this is **`pptx`**, already on disk and active in this session.

**pptx** — Anthropic-official (`source: anthropic`, shipped in the same set as `docx`, `xlsx`, `pdf`; the leaderboard's `anthropics/skills` repo sits at 100K+ installs). Installed at `/root/.claude/skills/synced/pptx`.

It triggers on any mention of "deck", "slides", "presentation", or a `.pptx` / `.potx` file, so on a normal week you just say "turn these reports into a deck" and it loads itself. Nothing to add to your config.

## What it actually gives you for this job

- **Deck generation** via `pptxgenjs`, with the footgun list that separates a deck that opens from one PowerPoint calls corrupt — hex colors without `#`, `pres.layout` set before slides, stacked-bar label positions, combo-chart axis declarations.
- **Native charts**, not screenshots — research reports usually carry numbers, and `addChart()` keeps them editable in PowerPoint.
- **Template-driven output** — point it at a `.potx`/`.pptx` house template and it unpacks, maps each report section onto a real layout, and repacks. This is the part that matters for a weekly cadence: same template every week, consistent decks, no drift.
- **Validation** — `scripts/office/validate.py` checks schema, relationships, and charts before you ever open the file, and `scripts/thumbnail.py` renders a labeled grid so layouts can be eyeballed.
- **Speaker notes** — worth using, since a research report has more prose than a slide should carry; the narrative goes in `addNotes()`.

Your markdown input needs no skill at all — reading and structuring markdown is native. `pptx` handles the output half, which is the hard half.

## Two things I'd want to know before the first run

I can't ask interactively, so answering these in your next message will save a round trip:

1. **Is there a house template?** A `.potx` or an existing branded deck changes the approach from "generate from scratch" to "fill a template" — the second gives far better-looking, more consistent results week over week.
2. **What's the shape of a report → deck mapping?** Roughly how many slides per report, and does each markdown `##` become a slide, or do you want a fixed skeleton (title / summary / findings / data / recommendations) that content gets fitted into? A fixed skeleton is what makes this repeatable.

## On the "every week" part

Since the skill is already permanent, the only thing left to automate is the trigger. Two options if you want it hands-off:

- **A Routine** — a scheduled prompt that fires weekly (e.g. Monday morning), picks up whatever markdown landed in a given folder, and produces the decks.
- **A thin local skill of your own** — `npx skills init report-to-deck` wrapping your template path, slide skeleton, and naming convention, so the recurring decisions stop being re-decided each week. It would call `pptx` for the mechanics.

Say the word and I'll set up either one, or just point me at this week's markdown files and I'll build the first deck so we can lock the format.

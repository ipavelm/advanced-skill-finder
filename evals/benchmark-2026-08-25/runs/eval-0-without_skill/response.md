# Yes — `pptx`, and it's already installed

You don't need to go hunting the ecosystem for this one. The skill that does markdown-in / PowerPoint-out is **`pptx`**, and it's already synced into your setup at `/root/.claude/skills/synced/pptx/` (also mirrored at `/mnt/skills/public/pptx/`). It triggers on its own whenever a `.pptx` is involved — so "turn this report into a deck" already picks it up without you naming it.

## What it actually gives you

It's not a thin wrapper around "write some slides." It's a build-and-verify pipeline:

| Stage | What the skill does |
|---|---|
| Build | Generates the deck with `pptxgenjs` (preinstalled), with a long list of hard-won footguns baked in — hex colors that silently corrupt the file, chart axis declarations PowerPoint rejects, shadow offsets, stacked-bar label positions |
| Template mode | Unzip a `.potx`/`.pptx`, duplicate and remap slides via `scripts/add_slide.py`, fill the XML, repack. This is the path you want if your reports go into a house-branded deck each week |
| Layout picking | `scripts/thumbnail.py` renders a labeled grid of every template slide so sections get mapped onto *varied* layouts instead of 20 identical title-and-bullets slides |
| Content QA | `markitdown output.pptx` to diff the text back against your markdown, plus a grep for leftover `lorem` / `[insert` / `XXX` placeholder text |
| File QA | `scripts/office/validate.py` — catches the specific malformed XML that opens fine in LibreOffice and python-pptx but makes real PowerPoint declare the file corrupt |
| Visual QA | Renders every slide to JPEG via LibreOffice + `pdftoppm` and inspects them for overflow, overlaps, bad margins, low contrast |

That last three-part QA loop is the part that matters for a weekly cadence. A deck that quietly fails to open in PowerPoint is the failure mode you'd hit otherwise, and `validate.py` names the fix for each fault rather than just flagging it.

It also carries real design opinion — ten content-informed color palettes, typography sizing, and an explicit "avoid" list (no accent lines under titles, no decorative color bars, no text-only slides) aimed squarely at the tells that make a deck look machine-generated.

## Two others worth pairing with it

- **`dataviz`** — if your research reports carry numbers. Load it before any chart so the deck's charts read as one system rather than defaulting to the PowerPoint palette. `pptx` keeps charts native via `addChart()`, so the two compose cleanly.
- **`pdf`** — for shipping a read-only copy alongside the `.pptx`.

## Making the weekly part actually weekly

The gap between "there's a skill" and "this is a five-minute Monday task" is the repeated decisions: which template, how your report sections map to slide layouts, your palette and fonts, how long a deck runs. Right now you'd re-specify those every week.

Two ways to close it, in order of how much I'd recommend them:

1. **Wrap your specific workflow in a small project skill** using `skill-creator`. It would encode your template path, your section-to-layout mapping, and your brand colors, then delegate the mechanics to `pptx`. After that, each week is "build this week's deck from `reports/2026-08-24/`." This is the high-value move and it's a one-time setup.
2. **Schedule it.** A Routine can fire weekly and run that skill against whatever landed in your reports folder, so the draft is waiting for you. Worth doing only after step 1 — an unattended run needs the workflow pinned down first.

## What I'd need from you to set that up

Non-interactive here, so I can't ask — but these are the answers that would let me build the wrapper skill in one pass:

- Where do the markdown reports live, and are they one file per deck or many files merged into one?
- Do you have a `.pptx`/`.potx` house template? If so, its path. If not, do you want a designed-from-scratch look, and is there a brand palette to follow?
- Roughly how long should a deck run, and is there a fixed spine (title / exec summary / findings / recommendation / appendix)?
- Do the reports contain tables or numeric data that should become native charts?

Point me at one representative report and your template and I'll build the deck plus the reusable weekly skill in the same pass.

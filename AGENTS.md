# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

Magic Slide is a Codex skill that generates polished, self-contained HTML presentations with Magic Move transitions. The skill uses a structured workflow with user checkpoints at search and outline stages.

## Core Architecture

### Generation Model

**Multi-phase workflow with user confirmation:**
1. Ask user about topic, aesthetic style, language, images
2. Ask if user wants web search (optional). If yes, run `scripts/websearch.py`
   first; agent/default web search is only a fallback after the script path
   fails or returns no usable results.
3. Generate outline with a Magic Move spine and get user confirmation (REQUIRED)
4. Write Brief Lite, including Magic Move content-relay motion grammar, in the conversation before coding
5. Read reference files, make a compact internal style/layout plan with primary/supporting Magic Move continuity, and generate all modular HTML sources directly
6. Merge slides into single HTML
7. Inject FLIP engine and runtime
8. Launch the Magic Slide preview server and fix objective QA failures

**Why this works:** User controls information gathering and reviews structure before generation. Brief Lite gives the deck an art direction without returning to the old long prototype loop. Read design guidelines once, generate all slides in main thread. Fast and simple with clear checkpoints.

### FLIP Animation Engine

Elements with matching `data-magic-id` animate smoothly between slides using the FLIP (First, Last, Invert, Play) technique. The engine is auto-injected by `inject-runtime.py`.

**Critical requirements:**
- Text elements with magic-id MUST have `display:inline-block` style
- Only assign magic-id where visible text is IDENTICAL on both slides
- No decorative elements should have magic-id

## Build Pipeline

### Core Scripts

All scripts are in `scripts/` directory:

**Generation & Assembly:**
- `merge-slides.py` — Combines modular sources into `[topic]/index.html`
- `inject-runtime.py` — Adds FLIP engine, navigation, progress bar, stagger animations
- `generate-image.py` — AI image generation via PipeLLM API
- `websearch.py` — Web search via PipeLLM WebSearch API

**Preview:**
- `serve.py` — Single-service preview server with deck-scoped routes

**Utilities:**
- `extract-slides.py` — Decomposes merged HTML back to modular sources

### Build Flow

```
1. Ask about web search (AskUserQuestion)
2. If user chooses yes, use scripts/websearch.py (PipeLLM WebSearch API) before
   any agent/default web search fallback
3. Generate sources/outline.md with Magic Move spine and confirm with user (AskUserQuestion - REQUIRED)
4. Write Brief Lite with Magic Move content-relay motion grammar in the conversation
5. Read reference files (generation-guide.md, layout-guide.md, html-contract.md, design-system.md, flip-engine.md; images.md when needed)
6. Read sources/outline.md
7. Generate a compact internal style/layout plan with primary/supporting Magic Move continuity, then create sources/ files directly (style.css, slide-01.html, slide-02.html, ...)
8. merge-slides.py combines them into index.html
9. inject-runtime.py adds FLIP + navigation to index.html
10. serve.py launches preview and remains running for user editing
```

### Running Scripts

```bash
# Merge slides
python3 scripts/merge-slides.py [topic]/sources/ --lang [language]

# Inject runtime
python3 scripts/inject-runtime.py [topic]/index.html --lang [language]

# Preview (MUST use this, not python3 -m http.server or file://)
python3 scripts/serve.py [topic]/index.html
```

Do not finish a deck-generation or deck-update task until the preview server is
running and the user has the displayed URL. The in-browser editor depends on
`scripts/serve.py`; opening the HTML file directly disables server-backed Save,
image replacement, and close/shutdown behavior.

For chat follow-up edits after a deck has been generated, treat `sources/` as
the source of truth: edit `[topic]/sources/style.css`,
`[topic]/sources/slide-XX.html`, or source-local helpers, then re-run merge and
inject. Do not patch `[topic]/index.html` directly unless the user explicitly
asks for a merged-HTML patch or the change comes from browser edit mode Save.

## File Structure

```
[topic]/
├── index.html                # Final self-contained presentation
├── assets/                   # Final presentation assets, if generated
│   ├── image-1.png
│   └── ...
├── sources/
│   ├── outline.md            # Presentation outline (generated first, user confirms)
│   ├── create_sources.mjs    # Optional generation helper, if used
│   ├── qa/                   # QA screenshots/reports, if generated
│   ├── style.css             # All CSS (variables, components, animations)
│   ├── slide-01.html         # Individual slide fragments
│   ├── slide-02.html
│   └── ...
```

Keep the topic root clean: only `index.html`, `assets/`, and `sources/`.

## Key Reference Files

**Core Documentation:**
- `references/design-system.md` — Aesthetic principles and design guidelines (from Anthropic's frontend-design skill)
- `references/generation-guide.md` — Generation instructions, Design Commitment Checklist, patterns
- `references/layout-guide.md` — Standard layout patterns and structure
- `references/html-contract.md` — Non-negotiable HTML/FLIP rules, including deck tone mode and root backgrounds
- `references/flip-engine.md` — FLIP animation internals
- `references/images.md` — Image generation guidelines

**All detailed rules (content density, HTML structure, magic-id usage, layout patterns, font sizing, etc.) are in these reference files. SKILL.md loads them during generation.**

## Runtime Prompt Maintenance

When changing skill instructions, avoid creating multiple full copies of the
same runtime rule. Keep each detailed rule in its authoritative reference file
and use short pointers elsewhere:

- Workflow/checkpoints: `SKILL.md` and `references/workflows/`
- Brief Lite format: `references/workflows/step-04-design-brief.md`
- Visual direction and anti-template rules: `references/design-system.md`
- Generation strategy: `references/generation-guide.md`
- Layout, overflow, source notes, and vertical balance: `references/layout-guide.md`
- HTML structure, deck tone mode, SVG, file naming, and verification checklist: `references/html-contract.md`
- Magic Move / `data-magic-id`: `references/flip-engine.md`
- Images, uploadable wrappers, and cover-image policy: `references/images.md`

If a rule needs to be mentioned outside its owner file, write a one-sentence
reminder plus a reference link. Do not paste the full rule into `SKILL.md`,
workflow steps, or this `AGENTS.md`.

## Design System Enforcement

**CRITICAL:** The design-system.md contains principles from Anthropic's official frontend-design skill. These MUST be enforced during generation.

**Before generating CSS/HTML, output Brief Lite covering:**
1. Aesthetic direction (Brutalist/Luxury/Playful/Editorial/etc.)
2. Typography strategy (Why this pairing? Is it overused?)
3. Color depth system (primary + soft + hot + muted variants)
4. Deck tone mode (primary light/dark + named inverse exceptions, if any)
5. Visual layers (base + atmosphere + texture)
6. Spatial composition (asymmetric/grid-breaking/overlapping)
7. Uniqueness check (Is this generic? First thing that comes to mind?)

Keep Brief Lite concise. Do not output the old long design brief unless the user
asks for high-touch design exploration.

**Hard stop:** for AI, infrastructure, investor, SaaS, and developer-tool decks,
do not default to dark/neon green, circuit-board traces, Matrix/cyber motifs,
terminal wallpaper, or ominous gradients. Those are generic and can feel
frightening. Use them only if the user explicitly asks for that mood.

**Common AI slop patterns to AVOID:**
- Font combos: Bebas Neue + Oswald + Montserrat, Playfair + Lato, Space Grotesk + Inter
- Colors: Purple + Cyan on dark, simple Black + Gold without variants
- Layouts: Everything centered, no asymmetry, no overlap

See `references/design-system.md` for complete list.

## Layout And SVG Reliability

- Do not generate `data-stagger="none"` as a default. Use `cascade` for most
  slides and `zoom-in` for covers/reveal beats. Slide-level `none` requires an
  explicit no-animation request and `data-stagger-disabled="true"`.
- Sparse slides should be vertically centered unless deliberately dense or top-aligned.
- Large split-layout headings need real width budgets (`minmax(0, ...)`, `min-width:0`, capped `clamp()` sizes) so they do not cover diagrams or cards.
- Card groups must use available slide width before shrinking text; see the
  usable-width/card-group rule in `references/layout-guide.md`.
- Source notes require reserved footer space.
- Inline SVG connector paths must include `fill="none"` and fallback stroke attributes directly on the path.
- Avoid complex SVG filters, masks, blend modes, `foreignObject`, and decorative filled path blobs.

## Post-Generation Editing

Users can edit the presentation in two ways, but agent-driven follow-up changes
must preserve the modular source files.

Editing requires the preview server from `scripts/serve.py`. Start it before
telling users to press `e` or use Save.

**1. Edit modular sources** (default for all agent changes):
- Edit `[topic]/sources/slide-XX.html` or `style.css`
- Re-run merge and inject scripts
- Refresh browser

**2. Edit merged HTML** (only for explicit quick fixes or browser edit mode):
- Press 'e' in browser to enter edit mode
- Click any text to edit inline
- Click "Save" to write changes back to `index.html`
- The preview server attempts to sync browser-saved changes back to `sources/`
- If editing `index.html` directly outside browser Save, warn that modular
  sources may become stale and prefer `sources/` instead

## Dependencies

- Python 3.7+
- No external Python packages required (uses stdlib only)
- Browser with JavaScript enabled for preview
- Optional: PipeLLM API key for image generation AND web search
  - Set via `PIPELLM_API_KEY` env var or `~/.config/pipellm/api_key`
  - Used for both `generate-image.py` and `websearch.py`
  - Web search: $0.05 per request
  - Image generation: varies by model

## File Naming Rules

**CRITICAL:** All file and folder names MUST be English-only (no CJK characters). This prevents URL encoding issues in the preview server.

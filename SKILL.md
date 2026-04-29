---
name: magic-slide
description: Generate a self-contained HTML presentation with Magic Move transitions. Use when the user wants to create a slideshow, presentation, or slide deck from a topic or outline, or invokes magic-slide preview to start the preview server.
argument-hint: "[preview <topic> | presentation request]"
---

# Magic Slide

Generate polished HTML presentations with smooth Magic Move transitions — elements that appear on multiple slides animate fluidly between their positions. Treat Magic Move as a story-planning constraint, not an afterthought: arrange the outline so meaningful labels, numbers, cards, images, or section markers can persist across adjacent slides.

## Skill Command Arguments

The user invoked this skill with: `$ARGUMENTS`

When invoked as `/magic-slide preview [topic]` in Claude Code or
`$magic-slide preview [topic]` in Codex, run the preview fast path:

1. Treat the argument after `preview` as the topic/deck directory. If omitted,
   use `.`. Preview the `index.html` inside that directory. If the user passes
   an explicit `.html` file, preview that file directly.
2. Locate this skill directory if needed:
   `SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)`
3. Start the preview server with the existing script:
   `python3 "$SKILL_DIR/scripts/serve.py" "$DECK_PATH"`
4. Keep the server process running and give the user the displayed URL.
5. Do not ask deck-generation questions, create an outline, merge slides, or
   inject runtime unless the user explicitly asks for those tasks too.

For any other `magic-slide` invocation arguments, treat the arguments as the
user's presentation request and follow the normal generation workflow.

## Non-Preview Intake Gate

Before running commands, searching, creating folders, writing an outline, or
generating slides for any non-preview deck request, complete Step 1 in
`references/workflows/step-01-requirements.md`.

Hard gate:
- If topic/audience-lens, aesthetic style, presentation language, or image
  policy is missing, inferred, or only implied, ask the Step 1 requirements
  question and stop.
- Do not treat the user's chat language as the presentation language.
- Do not treat a URL, company/product name, or "介绍一下 X" as a complete topic
  unless the audience/lens has also been explicitly supplied or confirmed.
- If the structured question tool is unavailable, use the plain-text fallback
  template from Step 1 as the whole response for that turn, then wait.

## CRITICAL: Script Execution Rules

**All scripts in this skill are located in the `scripts/` directory relative to the skill root.**

**When executing scripts:**
1. **If a script execution fails with "No such file or directory":**
   - DO NOT give up or tell the user "the script isn't available"
   - Find the skill directory using: `find ~ -name "magic-slide-skill" -type d 2>/dev/null | head -1`
   - Or search for SKILL.md: `find ~ -name "SKILL.md" -path "*/magic-slide-skill/*" 2>/dev/null | head -1 | xargs dirname`
   - Store the skill directory path in a variable
   - Re-execute the script using the absolute path: `python3 $SKILL_DIR/scripts/websearch.py`

2. **Always use absolute paths for script execution** to avoid path issues

**Example of correct execution:**
```bash
# Find skill directory (do this once at the start)
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)

# Execute scripts with absolute paths
python3 "$SKILL_DIR/scripts/websearch.py" "query"
python3 "$SKILL_DIR/scripts/generate-image.py" "prompt text" --output ./assets/image.png
python3 "$SKILL_DIR/scripts/merge-slides.py" ./sources/ --lang en
```

## CRITICAL: Injected Runtime Output Boundary

Treat `scripts/inject-runtime.py` and the behavior/results it injects into the
finished deck as Magic Slide runtime output. During deck generation, updates,
and QA, run the existing injector unchanged and preserve its injected behavior
by default. Do not edit the injector, patch injected runtime blocks in
`{topic}/index.html`, or add source CSS/HTML/JS whose purpose is to disable,
hide, neutralize, or override injected features unless the user explicitly asks
for that specific runtime behavior change.

Examples of prohibited "cleanup" without explicit user request: hiding the
animated/custom cursor, restoring the system cursor with `cursor: auto` or
`cursor: default`, removing or hiding navigation/progress/edit controls,
turning off Magic Move, suppressing injected stagger, or bypassing runtime fit.

If a deck has a visual or layout issue, fix the modular source files
(`sources/style.css` and `sources/slide-XX.html`) around the runtime behavior,
then re-run merge and inject. If the issue appears to be caused by injected
runtime behavior itself, report the suspected runtime issue or ask before
changing it; only modify runtime behavior when the user requested that change.

## Quick Workflow

**Default to the balanced path.** Keep the outline checkpoint, write a short
design brief, then generate the full deck in one production pass. Do not build
a separate prototype unless the user explicitly asks for that slower workflow.

**USER INTERACTION RULE:** All user confirmations MUST use the AskUserQuestion
tool. Text-based questions are ONLY a fallback if the tool is unavailable or
fails. Always try AskUserQuestion first. If you must fall back to plain text,
end structured questions with a copyable response template, except for outline
confirmation; see `references/workflows/text-question-templates.md`.

1. **Step 1: Gather requirements** — Ask ALL 4 question groups: topic/audience-lens, aesthetic style, **language** (REQUIRED - never infer from user's message language), images
2. **Step 2: Web search** — Ask user if they want online search (optional). If they say yes, run `scripts/websearch.py` first; built-in agent search is only a fallback after the script fails or returns no usable results.
3. **Step 3: Generate outline** — Create `{topic}/sources/outline.md` with MANDATORY elements: thesis spine, audience/lens, chapter arc, closing idea, and Magic Move spine. Get user confirmation (required checkpoint)
4. **Step 4: Write Brief Lite** — Output a compact design brief before CSS/HTML: visual world, rejected tropes, cover promise, tone mode, type/color/material logic, slide families, Magic Move motif and transition beats
5. **Step 5: Generate production sources** — Create `style.css` and all `slide-XX.html` files directly from the confirmed outline and Brief Lite, after making a continuity map for adjacent slide pairs
6. **Step 6: Merge slides** — Combine modular sources into single HTML
7. **Step 7: Inject runtime** — Run the existing injector unchanged; preserve injected behavior/results unless the user explicitly asks otherwise
8. **Step 8: Preview & final QA** — ALWAYS launch the skill preview server with `scripts/serve.py`, keep it running, and fix objective failures before delivery

**NON-NEGOTIABLE DELIVERY RULE:** After generating or updating a deck, do not finish until `python3 "$SKILL_DIR/scripts/serve.py" {topic}/index.html` is running and you have given the user the preview URL. Opening the HTML file directly is not enough: edit mode, save, image replacement, and close/shutdown controls require the Magic Slide preview server. Never substitute `python3 -m http.server`, `npx serve`, or a file URL for the skill server.

**NON-NEGOTIABLE UPDATE RULE:** When the user continues in chat after a deck has been generated and asks for changes, edit the modular source files first: `{topic}/sources/style.css`, `{topic}/sources/slide-XX.html`, and any source-local helpers. Then re-run `merge-slides.py`, re-run the existing `inject-runtime.py` unchanged, and refresh or restart the Magic Slide preview server. Do not edit `{topic}/index.html` directly for agent-driven follow-up changes unless the user explicitly asks to patch the merged HTML, or the change comes from the browser edit mode Save flow.

**Brief Lite is not optional.** It is the quality guardrail that prevents
generic or frightening template output. Keep it concise. Only use the slower
prototype gate when the user asks for high-touch design exploration, a risky
visual direction, or a small sample before generating the whole deck.

## Detailed Workflow Steps

Each step has detailed instructions in the `references/workflows/` directory. Read the relevant file when you reach that step:

- [Step 1: Gather Requirements](references/workflows/step-01-requirements.md) - **MUST ask ALL 4 question groups: topic/audience-lens, style, language (REQUIRED), images. Never skip language question.**
- [Step 2: Web Search](references/workflows/step-02-websearch.md) - Optional online search for current information
- [Step 3: Generate Outline](references/workflows/step-03-outline.md) - Create and confirm presentation structure
- [Step 4: Write Brief Lite](references/workflows/step-04-design-brief.md) - Compact required design brief before coding
- [Step 5: Generate Production Sources](references/workflows/step-07-generate.md) - Create `style.css` and all slides directly from the confirmed outline and Brief Lite
- [Step 6: Merge Slides](references/workflows/step-08-merge.md) - Combine modular sources into single HTML
- [Step 7: Inject Runtime](references/workflows/step-09-inject.md) - Run the existing injector and preserve injected behavior/results unless explicitly requested otherwise
- [Step 8: Preview & Final QA](references/workflows/step-10-preview.md) - Launch preview and verify quality

Legacy optional workflow files:
- [Optional: Build Visual Prototype](references/workflows/step-05-prototype.md) - Use only when the user requests a sample first
- [Optional: Pass Visual Gate](references/workflows/step-06-visual-gate.md) - Use only with the optional prototype workflow

## Post-Generation Editing

Users can edit the presentation in two ways, but agent-driven follow-up work
must preserve the source-of-truth files.

**Editing requires the preview server.** Before mentioning edit mode, ensure the deck is being served through `scripts/serve.py` and give the user the server URL. If the server is not running, start it first.

**1. Edit modular sources** (default for all agent changes):
- Edit `{topic}/sources/slide-XX.html` or `style.css`
- Re-run merge and inject scripts
- Refresh browser

**2. Edit merged HTML** (only for explicit quick fixes or browser edit mode):
- Press 'e' in browser to enter edit mode
- Click any text to edit inline
- Click "Save" to write changes back to `index.html`
- The preview server attempts to sync browser-saved changes back to `sources/`
- If editing `index.html` directly outside the browser Save flow, warn that the
  modular sources may become stale and prefer `sources/` instead

## File Structure

```
{topic}/
├── index.html          # Final merged presentation (deliverable)
├── assets/             # Final presentation assets (if generated)
│   ├── image-1.png
│   └── ...
└── sources/            # Process files and modular source files
    ├── outline.md      # Confirmed outline
    ├── create_sources.mjs  # Optional generation helper, if used
    ├── qa/             # QA screenshots/reports, if generated
    ├── style.css
    ├── slide-01.html
    ├── slide-02.html
    └── ...
```

Keep the topic root clean. Apart from `index.html`, `assets/`, and `sources/`,
all process artifacts belong inside `{topic}/sources/`.

## Key Reference Files

Read these files as needed during generation. Treat them as the single
authoritative source for their topic; do not reconstruct long versions of their
rules in this file or workflow steps.

- [design-system.md](references/design-system.md) — aesthetic direction and anti-template guardrails
- [generation-guide.md](references/generation-guide.md) — production planning and generation strategy
- [layout-guide.md](references/layout-guide.md) — layout primitives, overflow, vertical balance, and source-note placement
- [html-contract.md](references/html-contract.md) — required slide structure, deck tone mode, root backgrounds, SVG contract, file naming, and verification checklist
- [flip-engine.md](references/flip-engine.md) — Magic Move / `data-magic-id` planning and reliability rules
- [images.md](references/images.md) — generated image use, uploadable wrappers, and cover-image policy

## Design Philosophy

1. **Outline must be an argument, not a topic list** — Every slide advances a thesis, not just "this also exists"
2. **Brief Lite first** — Commit to a topic-specific visual world and primary light/dark tone before writing CSS. Keep it concise, but output it so the design promise is visible.
3. **Magic Move is planned early** — The outline should create overview/detail, chapter-marker, and recurring-anchor opportunities before HTML exists. Do not rely on decorative duplicates to manufacture motion late.
4. **Generate once, inspect once** — Produce the full deck after outline and Brief Lite, then use final QA to catch objective failures.
5. **Objective QA for objective failures** — Use tools for syntax, overflow, text contrast/readability, images, SVG rendering, and Magic Move, not subjective taste scoring.
6. **Cover is a special moment** — Slide 1 must be a distinct opening
   composition with concise cover copy. Use `design-system.md`, `images.md`,
   and `html-contract.md` for the detailed cover rules.
7. **Fast iteration** — If something's wrong, revise CSS and affected source slides quickly, then merge/inject again.
8. **Merged HTML is an artifact** — Treat `{topic}/index.html` as generated output. Direct HTML edits are only for explicit one-off patches or the browser edit mode Save flow.
9. **Layout reliability is mandatory** — Follow `layout-guide.md` for
   primitives, overflow, vertical balance, and source-note placement.

**Quality bar:** Every deck should feel distinctive and intentional, not like the first thing that came to mind. If another topic could use the same design unchanged, the design is too generic.

**Readability bar:** Treat unreadable text as a broken deck, not a taste issue.
Use `html-contract.md`, `layout-guide.md`, and `design-system.md` for the
detailed text contrast and text-fit rules.

## Output Quality

Every presentation should be:
- **Self-contained** — Single HTML file, no external dependencies
- **Smooth** — Magic Move creates fluid transitions
- **Portable** — Works offline, easy to share
- **Editable** — Modular sources for easy iteration
- **Distinctive** — Unique visual style, not generic AI aesthetics

The goal is speed with taste: decide the visual world, preview it early, then generate fast and iterate against the rendered deck.

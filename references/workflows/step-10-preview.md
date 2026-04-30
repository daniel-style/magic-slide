## Step 8: Preview & Final QA

### 10a. Launch preview

This step is mandatory. Do not skip it after generating or updating a deck.
The presentation's edit mode, Save button, image replacement, and close/shutdown
controls depend on the Magic Slide preview server. Opening `index.html` directly
or using a generic static server is not an acceptable substitute.

```bash
# Find skill directory
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)

# Start preview server (MUST use this script)
python3 "$SKILL_DIR/scripts/serve.py" {topic}/index.html
```

Keep this command running while the user previews or edits the deck. If the
command prints an existing service URL instead of starting a new foreground
process, use that URL. If the command fails because the skill directory was not
found, locate `magic-slide-skill` manually and re-run the same `serve.py` script
with an absolute path.

### 10a.1 QA overview gate

Run the runtime QA overview before detailed screenshots. This is an agent
quality gate, not an optional user aid.

1. Open the preview URL with `?ms_qa=overview`, or press `Q` in the running
   preview.
2. Prefer browser automation or Playwright: scroll the QA grid until every
   `.qa-card` has `data-scanned="1"`, then read `#qa-summary`, each card's
   `data-status`, and its `.qa-tag` labels.
3. If automation is unavailable, manually open QA overview, scroll through the
   full grid, and inspect `Issues only`.
4. Record the QA summary and issue tags in your working notes so the final
   response can report the outcome.

Triage rules:

- `FAIL` blocks delivery. Fix the modular source files, then re-run
  `merge-slides.py`, `inject-runtime.py`, `serve.py` if needed, and the QA
  overview gate.
- `WARN` requires full-size review. Fix actionable warnings; keep only named
  intentional exceptions, such as a deliberate inverse-tone display slide.
- QA overview flags high-signal heuristics: iframe/image load failures, visible
  overflow, runtime `.ms-fit-*` rescue classes, transparent root backgrounds,
  inset full-bleed background layers, card-contained text overflow, cramped
  multi-card rows, ordinary tone deviations, sparse framed panels, and adjacent
  `data-magic-id` text mismatches.
- QA overview is a first-pass radar. After it is clean, still do targeted
  full-size screenshots or rendered slide checks for the cover, dense/content
  slides, diagrams/images, and any formerly flagged pages. `low contrast text`
  is a failure: fix the source color/background pair rather than accepting it
  as a style choice.

### 10b. Final QA checklist

**Objective checks:**
1. All slides render without console-breaking errors.
2. `html-contract.md` passes: slide structure, root backgrounds, SVG, file names, and checklist items.
   Include the deck tone mode check: ordinary slides must stay in the primary
   light/dark mode, and inverse-tone slides must be named exceptions with a
   distinct display role.
   Check wide-screen coverage: cover/photo/material backgrounds must reach all
   four viewport edges and must not be bounded by `.slide-content` max-width.
3. `layout-guide.md` passes: no overflow, clipped text, collisions, unplanned top-heavy layouts, or source-note collisions.
   Treat cramped card rows with word-by-word wrapping as a failure when nearby
   horizontal space is empty; revise the source layout to use the available
   width or split the slide. QA overview tags `card text overflow` and
   `cramped card row` are blocking failures, not visual-taste warnings.
   Also treat card-title collisions as failures even when the text remains
   inside the viewport. In rendered review, scan metric/card grids for words
   crossing into neighboring cards, especially four-card rows inside split
   columns.
   Treat ordinary slides whose main content sits in the upper third with a
   large empty area below as failures. Remove `.slide-top` / `.slide-dense`,
   center the `.slide-content`, or redesign the primitive unless the content is
   genuinely dense enough to fill the height budget.
   Treat oversized framed panels around low-density content as failures per
   `layout-guide.md`; shrink the frame, remove it, or make the diagram complete.
4. `design-system.md` passes: visual world is specific, palette/readability are clean, and the cover is a distinct opening composition.
5. `images.md` passes when images are used: assets load, content images are integrated, and cover imagery follows policy.
6. `flip-engine.md` passes: Magic Move ids are semantic, adjacent, and animate smoothly.
   Compare the rendered deck against the continuity map created before HTML;
   final QA should catch implementation misses, not invent the Magic Move
   structure after the deck is already built.
7. Runtime controls work: arrows, space, click navigation, progress bar, slide counter, and edit mode.

**Subjective review:**
- Visual consistency across all slides
- Consistent light/dark tone across ordinary slides, with any inverse-tone
  moments reading as intentional story beats rather than random alternation
- Clear hierarchy and readability
- Distinctive aesthetic (not generic)
- Layout balance follows the production plan and `layout-guide.md`; ordinary
  slides should not look stranded near the top or padded out by a source note
- Strong cover: simple, spacious, memorable, and visibly different from
  ordinary content slides; the title is concise, and decorative layers frame it
  instead of crossing or weakening it
- Clean palette: no muddy gray wash, accidental fog overlay, or weak accent
  block
- Smooth pacing and flow
- Strong opening and closing

### 10c. Deliver to user

Tell the user:
- Preview is running at the displayed URL from `scripts/serve.py`
- Final HTML is at `{topic}/index.html`
- QA overview result, such as `QA overview: 40 slides, 0 fail, 0 actionable warn`
- Final assets, if any, are in `{topic}/assets/`
- They can edit sources in `{topic}/sources/` and re-run merge/inject
- Process files such as outline, helper scripts, and QA artifacts are kept in
  `{topic}/sources/` so the topic root contains only deliverables
- They can use edit mode (press 'e') for quick text changes while the preview server is running
- The HTML file is self-contained and portable

## Post-Generation Editing

Users can edit the presentation in two ways, but source files are the default
source of truth for agent-driven follow-up changes.

### Chat follow-up changes

When the user asks for changes in the conversation after a deck has already
been generated:

1. Edit `{topic}/sources/style.css`, `{topic}/sources/slide-XX.html`, and any
   relevant source-local helpers first.
2. Re-run merge:
   `python3 "$SKILL_DIR/scripts/merge-slides.py" {topic}/sources/ --lang {language}`
3. Re-run runtime injection:
   `python3 "$SKILL_DIR/scripts/inject-runtime.py" {topic}/index.html --lang {language}`
4. Refresh or restart the Magic Slide preview server and give the user the URL.
5. Re-run the QA overview gate. For pure text edits, at minimum confirm the
   touched slides did not gain new `FAIL` or actionable `WARN` items.

Do not patch `{topic}/index.html` directly for normal follow-up edits. The
merged HTML is generated output. Direct edits are allowed only when the user
explicitly asks to patch the merged file, or when the change comes from browser
edit mode Save.

### Browser edit mode

Browser edit mode is for quick text/image changes while the preview server is
running:

- Press 'e' in browser to enter edit mode
- Click any text to edit inline
- Click "Save" to write changes back to `index.html`
- The preview server attempts to sync browser-saved slide changes back to
  `sources/`

If browser-saved changes cannot be synced to `sources/`, treat `index.html` and
`sources/` as diverged: either run `scripts/extract-slides.py` to resync the
slide fragments, or make the same change in `sources/` and re-run merge/inject.

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
visual-review gate, not an optional user aid.

1. Open the preview URL with `?ms_qa=overview`, or press `Q` in the running
   preview.
2. Prefer browser automation or Playwright: scroll the QA grid until every
   `.qa-card` has `data-scanned="1"`, then capture the complete overview. If
   the QA grid has a scrollbar, use full-page capture or a top-to-bottom set of
   overlapping screenshots.
3. If automation is unavailable, manually open QA overview and scroll through
   the full grid while capturing all rows.
4. Review the screenshots as a visual wall. In working notes, list problem
   slides and reasons such as layout imbalance, text errors, awkward wrapping,
   muddy color, weak contrast, crowded cards, element collisions, broken-looking
   images, rough diagrams, or slides that visibly do not hold together.
5. Open problem slides at full size, fix the modular source files, then re-run
   `merge-slides.py`, `inject-runtime.py`, `serve.py` if needed, and the QA
   overview gate.

Triage rules:

- QA overview is a visual review wall, not a rule-based diagnostic surface.
  Cards should not contain pass/fail status labels or enumerated issue tags.
- Do not inject screenshot review notes back into QA cards or `index.html`.
  Keep the visual issue list in working notes, fix `sources/`, and report the
  repaired slides in the final response.
- After the overview pass, still do targeted full-size screenshots or rendered
  slide checks for the cover, dense/content slides, diagrams/images, and any
  slides that looked questionable in the visual wall.

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
   Treat cramped card rows with word-by-word wrapping as a visual issue when
   nearby horizontal space is empty; revise the source layout to use the
   available width or split the slide. Find these problems from the rendered QA
   overview wall and full-size screenshots, not from runtime-generated tags.
   Also treat card-title collisions as visual issues even when the text remains
   inside the viewport. In rendered review, scan metric/card grids for words
   crossing into neighboring cards, especially four-card rows inside split
   columns.
   Treat ordinary slides whose main content sits in the upper third with a
   large empty area below as visual issues. Remove `.slide-top` / `.slide-dense`,
   center the `.slide-content`, or redesign the primitive unless the content is
   genuinely dense enough to fill the height budget.
   Treat oversized framed panels around low-density content as visual issues per
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
- QA overview result, such as `QA overview: 40 slides captured for visual review`
- Visual issues found and repaired, by slide number, or a short note that the
  captured overview and targeted full-size checks did not reveal issues needing
  source changes
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
   touched slides still look correct in the overview.

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

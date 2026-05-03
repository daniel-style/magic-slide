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

Run the runtime QA overview before any later detailed screenshots. This is a
visual review wall and revision-note capture surface, not an automatic scoring
gate.

For a newly generated deck, the gate has three ordered phases:

1. **Autonomous overview-longshot pass.** Open the preview URL with
   `?ms_qa=overview&ms_qa_capture=1`. This capture mode turns the QA wall into
   a real scrollable page so a browser full-page screenshot becomes one tall
   image of all slide cards. Do not screenshot immediately after navigation:
   wait for the embedded slide iframes to finish loading and settle. The
   runtime readiness signal is `body.ms-qa-ready` with
   `body[data-ms-qa-pending="0"]`; `body[data-ms-qa-timeouts]` should also be
   `"0"` before capture, and `body[data-ms-qa-errors]` should be `"0"` unless
   you are explicitly investigating a frame load failure. In Playwright, wait
   for the selector/state, then wait a short extra frame-settle delay before
   `fullPage` screenshot. If cards are blank, still showing loading frames, or
   have timed out/errored, the screenshot is invalid for visual QA; wait/reload
   or inspect the affected slides before using it. Capture one
   full-page/scrolling QA overview screenshot first. If a tool cannot save one
   very tall image, capture the minimum number of vertical chunks of the QA
   wall; do not open every slide individually. Use that visual wall to identify
   the slide numbers with obvious rendered visual problems:
   layout overflow, clipped or cropped content, text/image overlap, cramped
   grids, unreadable text or weak color contrast, broken/cropped image
   treatment, weak cover framing, blank/unloaded cards, visibly unfinished
   diagrams, top-edge browser/address-bar-like chrome, Magic-only token rows,
   or global stage-fit failures from `layout-guide.md`. Fix those
   obvious issues in modular sources, re-run
   `merge-slides.py` and `inject-runtime.py`, refresh or restart `serve.py` if
   needed, and repeat the single QA overview longshot check until the
   first-pass visible problems are repaired. Do not capture full-size
   single-slide screenshots during this autonomous first pass; once the
   overview-longshot repairs are done, go directly to the mandatory user
   revision pause.
2. **Mandatory user revision pause.** After the autonomous pass, reopen or leave
   the deck in QA Overview and stop. Tell the user they can mark slide-level
   changes by clicking `Revise slide` on a QA card, entering a free-text note,
   saving it, and then returning to the conversation to say they are ready for
   you to continue. This pause is required after new deck generation; do not
   proceed to final QA or delivery until the user replies.
3. **Resume from saved revision notes.** When the user returns, read unresolved
   notes from `{topic}/sources/qa/visual-issues.json` first and make a set of
   known slide numbers. Those notes are the repair queue. For each marked
   slide, open the matching `{topic}/sources/slide-XX.html` plus
   `{topic}/sources/style.css` and repair the modular sources before taking any
   fresh screenshots. Use targeted screenshots only when a saved note is too
   ambiguous to interpret from JSON/source context. After source repairs,
   re-run `merge-slides.py`, `inject-runtime.py`, `serve.py` if needed, and the
   QA overview gate as verification; use that verification pass to inspect
   unmarked slides for additional problems. After visual verification,
   automatically mark repaired requests as `resolved: true` in
   `visual-issues.json`, with `resolvedAt`, `resolvedInRevision`,
   `resolution`, and `changedFiles`.

Revision notes are stored in `{topic}/sources/qa/visual-issues.json`. They are
human/agent visual review notes, not runtime diagnostics and not pass/fail
statuses.

QA cards also expose a `Resolve` button for manually marking an unresolved
slide note as fixed when the repair happened outside the normal agent resume
flow.

The mandatory user revision pause happens once after the autonomous first pass
for a newly generated deck. After the user returns and those notes are repaired,
later QA overview runs are verification passes unless the user explicitly asks
for another marking round.

Triage rules:

- QA overview is a visual review wall, not a rule-based diagnostic surface.
  Cards should not contain pass/fail status labels or enumerated issue tags.
- The overview longshot is judged page by page. Report and repair visual
  problems by slide number, focusing on rendered layout, readability, color
  contrast, image/diagram treatment, and whether any card is blank or unloaded.
- Revision notes are a source-first repair queue, not a reason to screenshot
  before fixing. Use screenshots before repair only when a saved note is
  ambiguous; otherwise repair marked source slides first, then screenshot the
  rendered deck for verification and missed issues on unmarked slides.
- During post-repair verification, skip already marked slides while discovering
  new screenshot issues so the same human note is not reported twice.
- Do not inject revision notes into `index.html`. QA cards only read/write
  `sources/qa/visual-issues.json`; the merged HTML remains generated output.
- Do not ask the user to clear resolved issues. The agent resolves them in JSON
  after repairing and visually verifying the relevant slides.
- For a newly generated deck, do not do targeted full-size screenshots after
  the autonomous overview-longshot repair pass; stop for the mandatory
  `Revise slide` marking pass. After the user returns, targeted full-size
  screenshots or rendered slide checks may be used only for slides that need
  closer inspection: marked revision slides, dense/content slides,
  diagrams/images, and any cards that still look questionable in the visual
  wall. Do not capture every slide individually by default.

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
   Check the design-canvas scaling rule in the QA overview wall: ordinary
   slides should preserve their intended 16:9 composition when scaled down into
   overview cards. Treat repeated edge-hugging titles, split panels drifting to
   opposite slide edges, stretched card rows with tiny islands, or source notes
   far from their related content as visual issues. Repair by grouping content,
   constraining the internal `.stage`, reducing split gaps, or redesigning the
   primitive; do not treat global `.slide-content` shrinkage as the default fix.
   Also check at least the active single-slide preview in a wide browser
   viewport: direct `.slide-content` must stay centered inside the injected
   1680px content canvas. If every slide suddenly looks very wide and loose in
   single-slide view but not in the QA cards, look for source CSS or inline
   styles overriding the runtime canvas guard (`max-width:none`, `width:100vw`,
   or a more specific `.slide-content` rule) and remove that override.
   Also apply `layout-guide.md`'s global stage-fit rule; those failures are
   visual issues even when nothing overflows.
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
   Treat repeated top strips, full-width brand pills, fake address bars, and
   direct-child slide chrome as visual issues. They often look like runtime
   bugs rather than slide design.
4. `design-system.md` passes: visual world is specific, palette/readability are clean, and the cover is a distinct opening composition.
5. `images.md` passes when images are used: assets load, content images are integrated, and cover imagery follows policy.
6. `flip-engine.md` passes: Magic Move ids are semantic, adjacent, and animate smoothly.
   Compare the rendered deck against the continuity map created before HTML;
   final QA should catch implementation misses, not invent the Magic Move
   structure after the deck is already built. Body token rows, focus chips, or
   labels whose main job is movement fail this check even if the animation is
   technically smooth.
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
- QA overview result, such as `QA overview longshot: 40 slides captured for visual review`
- Unresolved revision-note status from `{topic}/sources/qa/visual-issues.json`,
  if any remain
- Visual issues found and repaired, by slide number, or a short note that the
  captured overview and targeted full-size checks did not reveal issues needing
  source changes
- Final assets, if any, are in `{topic}/assets/`
- They can edit sources in `{topic}/sources/` and re-run merge/inject
- Process files such as outline, helper scripts, and QA artifacts are kept in
  `{topic}/sources/` so the topic root contains only deliverables
- They can use edit mode (press 'e') for quick text changes while the preview server is running
- The HTML file is self-contained and portable

At the mandatory user revision pause, do not use this final delivery checklist.
Give only the preview URL, the QA overview status, a short list of obvious
issues you already repaired, and the instruction to use `Revise slide` on QA
cards before asking you to continue.

## Post-Generation Editing

Users can edit the presentation in two ways, but source files are the default
source of truth for agent-driven follow-up changes.

### Chat follow-up changes

When the user asks for changes in the conversation after a deck has already
been generated:

1. Read `{topic}/sources/qa/visual-issues.json` first. If it contains unresolved
   revision requests, treat their slides as known repair targets. Open the
   matching source slides and CSS, then fix those known targets before taking a
   fresh QA overview longshot. Use screenshots before repair only when a note is
   too ambiguous to interpret from JSON and source context.
2. Edit `{topic}/sources/style.css`, `{topic}/sources/slide-XX.html`, and any
   relevant source-local helpers first.
3. Re-run merge:
   `python3 "$SKILL_DIR/scripts/merge-slides.py" {topic}/sources/ --lang {language}`
4. Re-run runtime injection:
   `python3 "$SKILL_DIR/scripts/inject-runtime.py" {topic}/index.html --lang {language}`
5. Refresh or restart the Magic Slide preview server and give the user the URL.
6. Re-run the QA overview gate as a verification pass. Use this rendered pass to
   confirm touched slides and inspect unmarked slides for additional issues. For
   pure text edits, at minimum confirm the touched slides still look correct in
   the overview.
7. If unresolved revision requests were repaired, update their JSON records to
   `resolved: true` with the repair revision and changed files.

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

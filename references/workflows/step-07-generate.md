## Step 5: Generate Production Sources

After the user confirms the outline and Brief Lite is written, generate the
production deck directly. Do not create a separate prototype unless the user
asked for that slower workflow.

### 5a. Read the core references once

Read:
- `generation-guide.md`
- `layout-guide.md`
- `html-contract.md`
- `design-system.md` for aesthetic guardrails and anti-template warnings
- `flip-engine.md` for Magic Move continuity and `data-magic-id` reliability
- `images.md` only if images are requested

### 5b. Make a compact internal production plan

Before writing files, make a concise internal plan based on Brief Lite:
- Chosen visual world and avoided generic tropes
- Dedicated cover composition and why it differs from slide 2
- Cover simplicity gate: for company/product/AI/infrastructure/SaaS/
  developer-tool decks, confirm slide 1 is title-led with only simple
  non-text decoration plus optional terse labels/chips; any process flow,
  request pipeline, architecture diagram, or explanatory cards move to slide 2
  or later.
- Full-viewport background ownership: which visual fields live on the root
  `.slide`, which full-bleed layers are direct `.slide > .bg` children, and
  which images are ordinary content images. No apparent background may be inside
  `.slide-content` or another max-width wrapper.
- Slide chrome gate: confirm each slide has exactly one real `.slide-content`
  direct child plus optional `.bg` direct children only. Do not plan
  browser/address-bar-like top strips, full-width brand pills, or direct-child
  `brand-mark` / `section-no` chrome.
- Cover copy split: concise H1 plus any terse subtitle/chips needed for scope
- Primary deck tone mode and named inverse-tone exceptions, if any
- Slide family/primitives
- Type/color/material logic, including the style-to-type contract from
  `design-system.md`: display/body/optional mono stacks, why the type fits the
  requested style, and any language/script adjustments
- Footer/source-note strategy
- Design-canvas scaling strategy from `layout-guide.md`: keep `.slide-content`
  as the stable 16:9 design-canvas wrapper and rely on runtime/overview scaling
  for rendered sizes; use internal stages, groups, panels, and evidence bands
  to make individual slides feel tight.
- Stage-fit map from `layout-guide.md`: for each slide family, choose compact
  stage, wide evidence band, or full visual frame before writing HTML.
- Width allocation for card groups, comparison cells, and evidence bands,
  especially where a split layout would otherwise squeeze cards into one column
- Card-count gate for split layouts: if one half of a horizontal split would
  contain three or more metric/text cards, move the card group to a full-width
  evidence band, use a Metrics/Grid slide, or split the content. Do not make
  four-card metric grids inside a half-width column.
- Card-grid parity gate: known even card counts must use explicit symmetric
  grids, not automatic column counts that can orphan one card. Four cards must
  render as `2x2`, six as `3x2` or `2x3`, and eight as `4x2` or `2x4` unless
  the group intentionally stacks as one column at a breakpoint. If a split
  column cannot support the symmetric grid with readable card widths, move the
  card group to a full-width evidence band or split the slide.
- Framed-content occupancy for main visuals, using `layout-guide.md`: a large
  bordered panel must have a real filled diagram/composition, not a tiny row
  inside an empty frame.
- Magic Move continuity map for every adjacent slide pair: content
  relationship, primary vs supporting anchors, planned `data-magic-id` names,
  exact visible text, source/target element type, source/target visual role,
  wrap policy (`nowrap` label vs matching multiline heading/body), and
  intentional hard cuts. The map must identify real content anchors, not
  appended focus-token rows or labels created mainly for motion.
- Slides that need diagrams, images, dense text, or split treatment
- Slides, if any, that truly need top alignment, with a reason. Default every
  slide to vertically centered content; only dense matrices/tables/timelines
  should opt into top alignment, and only when the main content fills most of
  the usable height.

Keep this plan compact. It is an authoring aid, not a conversation checkpoint.
Do not treat this as a QA checklist after generation. If the map is weak before
HTML exists, revise the slide sequence or treatment first; that is much cheaper
than rebuilding a finished deck.

### 5c. Generate all source files

Create `{topic}/sources/style.css` and every `{topic}/sources/slide-XX.html`
from the confirmed outline and Brief Lite. Any helper scripts, drafts, QA
notes, or intermediate files created during generation must also live under
`{topic}/sources/`, not in the topic root.

**Maintain consistency:**
- Use the same CSS variables and classes
- Follow the same layout patterns
- Maintain the same visual language
- Implement the Brief Lite type promise in `style.css`. Define explicit
  `--font-display`, `--font-body`, and `--font-mono` variables, apply them to
  the hierarchy, and tune weights, case, line height, and label/data treatment
  so the chosen aesthetic is visible in typography, not only in colors.
- Keep ordinary slides in the primary deck tone. Generate inverse-tone slides
  only when they were named in Brief Lite or the internal production plan.
- Build the Magic Move spine from the outline's content relay instead of
  sprinkling ids after the deck is done. Most adjacent pairs with continuous
  subject matter should share a primary semantic anchor; overview/detail or
  zoom-in sequences should often add 1-3 supporting anchors. Use hard cuts only
  for clear chapter breaks, tone shifts, or visual resets.
- Prefer semantic recurring elements that are already central to the body:
  heading phrases, agenda/list items, product/entity names, key numbers, dates,
  image frames, diagram nodes, comparison rows, and card titles. Treat short
  deck marks, chapter chips, footer marks, and brand chrome as non-magic by
  default. Do not use decorative blobs, ghost marks, invented duplicates, or
  body token rows as Magic Move targets.
- Keep short Magic Move labels stable while moving. For short content labels
  such as timeline dates, status badges, row labels, card tags, or diagram node
  labels, use `data-magic-nowrap="true"` or an approved label class and ensure
  both source and target share a one-line width policy. This is only for labels
  that are already necessary content; do not create labels or token rows merely
  so they can move. Do not let a label wrap during the clone animation and then
  snap back to one line on cleanup.

**Avoid repetition:**
- Vary layout primitives across slides
- Don't use the same primitive more than 3 times in a row
- Mix content densities and visual treatments

**Avoid known failure modes:**
- Apply `design-system.md` for anti-template, palette, typography, and cover
  concept guardrails.
- Apply `layout-guide.md` for primitives, text fit, collision budgets, vertical
  balance, and source-note placement.
- Do not leave large horizontal dead zones while text cards overflow or wrap
  word-by-word. Use the slide width, convert cramped card rows into full-width
  evidence bands, or split the slide.
- Do not solve a loose-looking slide by globally shrinking `.slide-content` or
  making it heavily `vw`-dependent. In QA overview, repeated edge-hugging
  headings, panels at opposite corners, or tiny card islands scattered across
  the slide are layout failures. Fix the internal primitive instead: group
  related items, reduce split gaps, wrap card rows in a shared panel, constrain
  a `.stage`, or redesign the slide.
- Apply `layout-guide.md`'s global stage-fit rule so sparse content does not
  default to repeated full-width trays.
- Do not leave an orphan final row in a known even card group. Avoid
  `auto-fit`/`auto-fill` for four-card and six-card groups unless QA proves the
  rendered breakpoint cannot produce `3+1` or `5+1`.
- Do not wrap a low-density mini-flow, chip row, or few small nodes in an
  oversized `visual-card`/panel. Apply `layout-guide.md`'s framed content
  occupancy rule.
- Do not use large metric-value styling for long words in narrow cards. If a
  metric value is a word/phrase, size it as a card heading from the container
  width, allow wrapping, or give it a wider card. Cards whose titles overlap
  neighboring cards are broken even if every text rectangle remains inside the
  viewport.
- Do not add `.slide-top`, `.slide-dense`, or a top-aligned root class to
  ordinary evidence, scorecard, KPI, comparison, or split slides. Top alignment
  is reserved for content that genuinely occupies the height budget; otherwise
  the source must stay vertically centered.
- Apply `html-contract.md` for slide structure, root backgrounds, SVG, file
  naming, deck tone mode, and final verification.
- Do not put visible chrome such as `.brand-mark`, `.section-no`, page counters,
  or label rails as direct children of `.slide`. Direct children should be
  `.slide-content` plus optional `.bg` layers only. Avoid long thin top bars,
  fake address bars, and full-width brand pills entirely.
- Apply `images.md` before generating or placing images, including cover-image
  and uploadable-wrapper policy.
- If a slide uses a cover/photo/material background, implement it as the root
  `.slide` background or a direct `.slide > .bg` layer before `.slide-content`;
  do not generate `.slide-content > .cover-image` or similar max-width-bounded
  background layers.
- Apply `flip-engine.md` for Magic Move continuity and `data-magic-id` usage.
- If the confirmed outline does not provide enough legitimate shared anchors,
  revise the slide treatment before writing HTML: turn a flat list into an
  index-to-detail sequence, split an overloaded slide into setup/detail, or
  carry a real heading phrase, card title, metric, diagram node, or key number
  forward. Keep visible text identical for shared ids.
- If a shared text anchor would be one line on one slide and multiline on the
  other, either make both sides share the same line-break behavior, add
  `data-magic-nowrap="true"` for a short label that genuinely fits, or move the
  `data-magic-id` to a shorter stable token. Do not animate the outer wrapper
  of a card/panel when its internal text reflows between roles.
- Hard stop before HTML: if the continuity map mostly relies on a footer,
  corner label, tiny deck mark, watermark, or pure chapter chip, revise the
  slide order or treatment until the primary anchors are content-bearing. A
  supporting anchor can reinforce continuity, but it cannot replace the primary
  content relay.
- Hard stop before HTML: if the proposed implementation uses `.focus-token`,
  token rows, "magic labels", pills, or chips appended near the bottom of body
  slides mainly as transition handles, remove that system and move the
  `data-magic-id` plan back onto real content.

### 5d. Handle images (if requested)

If the user requested AI-generated images:

```bash
# Find skill directory
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)

# Generate each image
python3 "$SKILL_DIR/scripts/generate-image.py" "detailed image prompt" \
  --output {topic}/assets/image-1.png \
  --model flux-1.1-pro

# Reference in slide HTML
<img src="assets/image-1.png" alt="description">
```

See `images.md` for image prompt guidelines.

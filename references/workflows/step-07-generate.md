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
- `flip-engine.md` only as needed for Magic Move continuity
- `images.md` only if images are requested

### 5b. Make a compact internal production plan

Before writing files, make a concise internal plan based on Brief Lite:
- Chosen visual world and avoided generic tropes
- Dedicated cover composition and why it differs from slide 2
- Slide family/primitives
- Type/color/material logic
- Footer/source-note strategy
- Magic Move continuity map
- Slides that need diagrams, images, dense text, or split treatment

Keep this plan compact. It is an authoring aid, not a conversation checkpoint.

### 5c. Generate all source files

Create `{topic}/sources/style.css` and every `{topic}/sources/slide-XX.html`
from the confirmed outline and Brief Lite. Any helper scripts, drafts, QA
notes, or intermediate files created during generation must also live under
`{topic}/sources/`, not in the topic root.

**Maintain consistency:**
- Use the same CSS variables and classes
- Follow the same layout patterns
- Maintain the same visual language
- Continue Magic Move motifs where applicable

**Avoid repetition:**
- Vary layout primitives across slides
- Don't use the same primitive more than 3 times in a row
- Mix content densities and visual treatments

**Avoid known failure modes:**
- Do not use black/dark + neon green/cyan + circuit-board/network wallpaper as
  the default visual language for AI, infrastructure, or developer-tool decks.
  That reads as generic and can feel frightening.
- Do not let one brand color wash over every surface. Accent colors need jobs:
  status, route, risk, highlight, or section state.
- Do not generate muddy palettes: low-saturation blue/green/gray fields,
  broad translucent white fog over dark slides, weak colored badges, or gray
  text on saturated accent blocks.
- Do not put white, cream, pale-gray, or low-opacity text on light/paper/canvas
  slides. Light fields require dark ink; pale text belongs only on dark fields.
- Do not use opacity below `0.72` or rgba/hsla alpha below `0.72` for real
  content text. If secondary copy needs hierarchy, choose a readable muted token.
- The cover must fulfill the Brief Lite cover promise. A huge title over a
  generic tech background fails.
- If the cover uses a subject image, frame it as full-bleed hero art, a wide
  hero panel, a mostly visible product/object, or an abstract material field.
  Do not place a landscape image in a tall narrow column with `object-fit:cover`
  where it becomes a random vertical strip.
- The cover must not reuse the same skeleton as ordinary content slides. Avoid
  title-left/card-grid-right, memo grids, dense tables, and normal two-column
  evidence layouts on slide 1 unless the user explicitly asked for a utilitarian
  report cover.
- Do not place sparse content near the top. Use `.slide-dense` only for slides
  whose main content genuinely needs top alignment because it nearly fills the
  viewport.
- Do not let headings, diagrams, cards, or source notes overlap. Split the slide
  or reduce the max heading size instead.
- In cards, timeline cells, phase boxes, lanes, and comparison panels, size
  headings from the component width with `container-type:inline-size` and `cqw`
  or a conservative max. Long labels must wrap or shrink before they collide
  with neighboring cards.
- Do not hide card overflow with `overflow:hidden`, clipping, masks, fades, or
  low opacity. Visible overflow means the slide is over budget and must be
  redesigned.
- For inline SVG connectors, add explicit `fill="none"` and fallback stroke
  attributes on every open path.
- Avoid complex SVG filters, masks, blend modes, `foreignObject`, and decorative
  filled blobs.

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

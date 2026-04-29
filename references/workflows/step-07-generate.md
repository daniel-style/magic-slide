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
- Primary deck tone mode and named inverse-tone exceptions, if any
- Slide family/primitives
- Type/color/material logic
- Footer/source-note strategy
- Width allocation for card groups, comparison cells, and evidence bands,
  especially where a split layout would otherwise squeeze cards into one column
- Magic Move continuity map
- Slides that need diagrams, images, dense text, or split treatment
- Slides, if any, that truly need top alignment, with a reason. Default every
  slide to vertically centered content; only dense matrices/tables/timelines
  should opt into top alignment.

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
- Keep ordinary slides in the primary deck tone. Generate inverse-tone slides
  only when they were named in Brief Lite or the internal production plan.
- Continue Magic Move motifs where applicable

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
- Apply `html-contract.md` for slide structure, root backgrounds, SVG, file
  naming, deck tone mode, and final verification.
- Apply `images.md` before generating or placing images, including cover-image
  and uploadable-wrapper policy.
- Apply `flip-engine.md` for Magic Move continuity and `data-magic-id` usage.

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

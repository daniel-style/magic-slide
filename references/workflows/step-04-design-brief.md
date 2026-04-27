## Step 4: Write Brief Lite

Brief Lite is required. It is the small design checkpoint that keeps Magic Slide
from falling into generic, frightening, or topic-swappable templates. Keep it
concise; do not return to the old long design-brief workflow unless the user
asks for deep exploration.

### 4a. Read Only What You Need

Read:
- `design-system.md`
- `generation-guide.md`
- `layout-guide.md`
- `html-contract.md`
- `{topic}/sources/outline.md`

Read `flip-engine.md` only when Magic Move continuity is central, and
`images.md` only when images are requested.

### 4b. Output Brief Lite Before CSS/HTML

Write a short brief in the conversation before creating `style.css` or slide
HTML. Target 120-220 words. Use this exact shape:

```markdown
**Brief Lite**
Audience/setting: ...
Visual world: ...
Rejected tropes: ...
Cover promise: ...
Type/color/material: ...
Slide families: ...
Magic Move motif: ...
```

Rules:
- For Auto style, name 2-3 plausible visual worlds and reject all but one in a
  sentence. This can still fit inside the brief.
- Make the visual world specific enough that another company or topic could not
  use it unchanged.
- Name at least two rejected tropes.
- Cover promise must describe the first slide's composition, not just mood.
- Cover promise must make slide 1 a distinct opening image: name its focal
  object, scale move, material/image/typographic treatment, and how it differs
  from ordinary content slides.
- Type/color/material must assign jobs to colors; do not let one brand color
  dominate every surface.
- Type/color/material must include a palette hygiene promise: the dominant field
  hue or material, the high-contrast accent treatment, and what prevents the
  deck from becoming gray, foggy, or washed out.
- Slide families must include at least four roles, such as thesis hero,
  evidence/data, system diagram, risk map, integration map, timeline, quote, or
  closing.

### 4c. Hard Stop Anti-Template Check

Before writing CSS, reject the brief and revise it if it depends on:
- Black or very dark background plus neon green/cyan as the main idea.
- Circuit-board, Matrix, cyber tunnel, abstract network, glowing grid, or
  "AI brain" wallpaper.
- A huge title over a generic generated tech background.
- A cover that reuses the same two-column, card-grid, memo-panel, table, or
  ordinary system-diagram layout as the content slides.
- Brand-color wallpaper where every chip, rail, heading, and image wash uses
  the same color.
- Low-saturation gray/blue/green wash as the whole visual idea, especially with
  translucent white fog over dark slides or gray text on colored focal blocks.
- Condensed all-caps display type plus ominous dark gradients unless the user
  explicitly requested a scary/dystopian mood.

For investor, SaaS, infrastructure, and developer-tool decks, prefer calm
editorial, operating manual, market memo, architecture monograph, product
teardown, or field-notebook directions over cyber/noir dashboards unless there
is a strong topic-specific reason.

### 4d. Continue

After Brief Lite, create `{topic}/sources/style.css` and all slides using
`references/workflows/step-07-generate.md`.

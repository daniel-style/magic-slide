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
Tone mode: primary [dark/light]; inverse exceptions: [none / slide numbers + role]
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
- If the cover uses linework, particles, nodes, traces, or pseudo-diagrams,
  Cover promise must name the quiet text zone; see `layout-guide.md`.
- Default cover promise must be no-image: a premium minimalist CSS material
  field built from restrained gradients, subtle pattern or texture, typography,
  and whitespace. It must read as grand, calm, simple, and high-end at first
  glance.
- Do not plan a generated/photo background for the cover unless the user
  explicitly asked for cover imagery or the topic requires a recognizable
  product/place/object on slide 1.
- If the cover uses an image, Cover promise must say how the image is framed:
  full-bleed, wide hero panel, mostly visible object/product, or abstract
  material. Do not allow a skinny cropped image strip, low-information object
  sliver, or ordinary uploadable image wrapper as the cover visual.
- Tone mode must name the primary deck tone (`dark` or `light`) and the inverse
  exceptions. Default to `inverse exceptions: none`; only name exception slides
  when they have a special story/display role as defined by `html-contract.md`.
  Do not choose mixed/alternating tone just to create visual variety.
- Type/color/material must assign jobs to colors; do not let one brand color
  dominate every surface.
- Type/color/material must include a palette hygiene promise: the dominant field
  hue or material, the high-contrast accent treatment, and what prevents the
  deck from becoming gray, foggy, or washed out.
- Type/color/material must include a readability promise: dark ink on light
  fields, light ink on dark fields, no pale/low-opacity real text, and
  container-sized card titles where labels may be long.
- Slide families must include at least four roles, such as thesis hero,
  evidence/data, system diagram, risk map, integration map, timeline, quote, or
  closing.

### 4c. Hard Stop Anti-Template Check

Before writing CSS, reject the brief and revise it if it depends on:
- Black or very dark background plus neon green/cyan as the main idea.
- Circuit-board, Matrix, cyber tunnel, abstract network, glowing grid, or
  "AI brain" wallpaper.
- A huge title over a generic generated tech background.
- A cover whose main impact depends on a generated/photo background image when
  the user did not explicitly ask for cover imagery.
- A cover that reuses the same two-column, card-grid, memo-panel, table, or
  ordinary system-diagram layout as the content slides.
- A cover that places a landscape/generated subject image in a tall skinny
  column, creating a random vertical crop or low-information object slice.
- Brand-color wallpaper where every chip, rail, heading, and image wash uses
  the same color.
- Low-saturation gray/blue/green wash as the whole visual idea, especially with
  translucent white fog over dark slides or gray text on colored focal blocks.
- White, cream, pale-gray, or translucent text on a light/paper/canvas field.
- Condensed all-caps display type plus ominous dark gradients unless the user
  explicitly requested a scary/dystopian mood.

For investor, SaaS, infrastructure, and developer-tool decks, prefer calm
editorial, operating manual, market memo, architecture monograph, product
teardown, or field-notebook directions over cyber/noir dashboards unless there
is a strong topic-specific reason.

### 4d. Continue

After Brief Lite, create `{topic}/sources/style.css` and all slides using
`references/workflows/step-07-generate.md`.

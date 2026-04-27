# Generation Guide - Magic Slide HTML

Use this guide with `design-system.md`, `layout-guide.md`, `html-contract.md`,
`flip-engine.md`, and `images.md`.

The generation process has two jobs:

1. Make a visually specific deck from Brief Lite.
2. Keep the HTML, layout, images, and Magic Move behavior reliable.

Do not use scripts, selector counts, color counts, gradient counts, or static
pattern matching to judge subjective design quality. Use tools for objective
checks only.

## Brief Lite First

Before coding, output the Brief Lite required by
`references/workflows/step-04-design-brief.md`. Keep it short enough to preserve
context and speed, but make it visible in the conversation so the visual promise
can be checked before generation.

The brief must cover:

- Audience, setting, and the one-sentence thesis.
- Chosen visual world and one rejected generic trope.
- Typography, color, material, and depth logic.
- Palette hygiene: how the dominant field avoids gray fog, how accent blocks
  keep contrast, and which overlays/tints are forbidden.
- The slide families/primitives the deck will use.
- The recurring detail system: source notes, captions, rails, callouts, diagram
  labels, data treatments, or image crops.
- Cover composition promise, including how slide 1 will be visually distinct
  from slide 2 and from ordinary content slides.
- Magic Move motifs that can persist across adjacent slides.

If the visual world could be reused unchanged for another topic, it is too
generic. Revise it before writing CSS, but keep the revision concise.

If the brief's visual drama mainly comes from a dark field, neon green/cyan,
circuit-board lines, glowing grids, abstract networks, or a generated "AI
infrastructure" wallpaper, reject it unless the user explicitly asked for that
look. For infrastructure and investor decks, calm specificity usually beats
ominous futurism.

If the color system mainly depends on low-saturation blue/green/gray gradients,
broad translucent white fog, gray text on colored panels, or colored blocks
with same-hue dark text, reject it and choose a cleaner material system before
writing CSS.

If the cover promise could be implemented as a normal title-plus-cards or
two-column content slide, reject it. Slide 1 needs a display idea before the
deck enters its working layouts.

## Outline Is An Argument, Not An Encyclopedia

The outline should already contain a point of view. For company, technology,
finance, or product decks, do not make a slide list that simply walks through
history, products, divisions, partnerships, and future vision. That usually
produces a competent but generic explainer.

Before slide titles, write:

- The one-sentence thesis the deck proves.
- The audience lens: investor, executive, student, builder, customer, public
  explainer, or another concrete setting.
- The chapter arc: what each section changes in the audience's understanding.
- The closing idea, so the deck does not end with a generic slogan.

Each slide should either advance the thesis, provide evidence, create a useful
contrast, or resolve a risk/question. If a slide only says "also this exists",
merge it, cut it, or turn it into a sharper evidence slide.

## Slide Budget Pass

Before writing HTML, convert the outline into a budgeted production plan:

```text
Slide 15 / professional-viz
Primitive: comparison OR metrics, not both
Focal element: workstation use case map
Support: 3 industries OR 3 differentiators
Detail: source note in reserved footer
Split if: metrics row is also needed
```

Use this pass to prevent overflow and flat hierarchy. A slide that wants a
title/subtitle block, two dense lists, three metric cards, and a source note is
not "rich"; it is overloaded. Split it into an explanation slide plus a metric
slide, or choose the one point the audience should remember.

The slide budget is a planning aid, not a subjective scoring script. It protects
the viewport and forces editorial choices before CSS tries to rescue the page.

By default, generate `style.css` and every `slide-XX.html` file directly after
this pass. A separate prototype gate is optional and should only be used when
the user asks to see a sample first or the visual direction is unusually risky.

## Core Slide Principles

1. **One slide, one idea.** Split content that cannot fit cleanly.
2. **One primary layout primitive per slide.** Choose it before writing HTML.
3. **Slide 1 is a distinct cover moment.** It should be simpler, larger, and
   more memorable than ordinary content slides.
4. **Visible hierarchy.** Each slide needs a clear focal element and supporting
   context.
5. **Purposeful variety.** Repetition is allowed only when it creates a
   deliberate sequence.
6. **Magic Move continuity.** Reuse semantic elements across adjacent slides
   when the story naturally continues.
7. **Text fits by design.** Do not rely on runtime rescue, hidden overflow, or
   manual browser edits.

## Cover Distinction

Before writing `slide-01.html`, define its display role separately from the
deck's normal slide families. The cover should be a title sequence frame,
poster, product reveal, book cover, exhibition wall, hero image, or simplified
symbolic system map.

Avoid cover structures that look like ordinary content slides:
- title left + card grid right
- normal two-column explanation
- dense product map
- memo grid / table / metrics row
- the same system diagram that appears again later

Safer cover patterns:
- large title/wordmark with one iconic object or diagram fragment
- full-bleed image/material surface with text over it
- oversized typographic crop plus a small subtitle/source mark
- one simplified symbolic diagram with generous whitespace
- dramatic single metric or quote only when it is the deck's thesis

When the cover and slide 2 are shown together in overview thumbnails, they must
read as different roles. Similar colors are fine; similar skeletons are not.

## Layout Reliability

For every slide:

1. Choose one approved primitive from `layout-guide.md`.
2. Name the focal element.
3. Name the one or two supporting blocks.
4. Decide whether each text block wraps or stays on one line.
5. Set real width budgets for large numbers, labels, captions, and titles.
6. Reserve a place for source notes, captions, or legends when they are needed.
7. Only then write the HTML.

If a slide needs two root layouts at once, split it into two slides.

### Full-Bleed Background Reliability

The root `.slide` is the page. Its background must cover the entire viewport in
normal view, exported screenshots, and overview thumbnails. Do not simulate a
background with a colored `.slide-content`, `.stage`, large card, or centered
panel; that creates visible borders when the runtime scales slides into
thumbnail iframes.

Use this pattern:

```css
.slide {
  position: relative;
  isolation: isolate;
  background:
    linear-gradient(...),
    var(--field);
  background-size: cover;
}

.slide::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.slide-content {
  position: relative;
  z-index: 1;
}
```

QA must include the overview grid. If a slide appears as an inset rectangle,
paper frame, unintentional border, or small washed panel inside the thumbnail,
the slide is broken; move the background to `.slide` and regenerate CSS.

### Palette Reliability

Treat muddy color as a generated-deck failure. A palette can be restrained, but
it still needs clear temperature, contrast, and color roles.

Rules:
- Avoid large translucent white or gray overlays on dark slides unless they are
  a visible material texture. They often turn dark fields into cloudy
  gray-green screenshots.
- Do not put dark same-hue text on saturated accent rectangles. Use light text
  on strong accents, or dark text on pale tints.
- Keep neutrals tinted toward the visual world instead of default gray. Warm
  paper, cool blueprint, ink-dark, and archival neutral are different fields;
  generic gray is not an art direction.
- Give each accent a job: route/control, state, chapter, risk, product surface,
  or focal call.
- Check the cover, a normal evidence slide, and an accent slide in rendered
  screenshots. If the screenshot looks foggy or dirty at a glance, revise CSS
  variables and overlay layers first.

For grid or flex columns that contain large titles, constrain text to the
column, not just to a character count. A safe pattern is
`minmax(0, ...)` on the track, `min-width:0` on the child, and
`max-inline-size:min(100%, 18ch)` on title blocks. Otherwise a display heading
can overflow its grid cell and visually collide with cards or diagrams.

### Sparse Slide Centering

Slides with little content should feel intentionally centered, not stranded near
the top. If the main content has one title/subtitle pair, one small diagram, or
one short list:

- Do not add `slide-dense`, `slide-top`, or a `justify-content:flex-start`
  override.
- Keep the main `.stage` or primary layout container vertically centered inside
  `.slide-content`.
- If a source note is needed, reserve footer space with padding, but keep the
  primary content centered in the remaining visual field.
- Runtime may add `.ms-sparse-balance` to repair accidental top alignment, but
  source slides should still be authored centered. If runtime adds
  `.ms-fit-top` or `.ms-fit-scale`, treat it as a layout bug, not a successful
  rescue.

### Collision Budget

Before writing each two-column or diagram slide, estimate whether the largest
heading can fit its column without covering the visual side.

- If a heading is longer than four display lines, reduce the max font size,
  widen the text column, or split the slide.
- Cap large split-layout headings with `max-inline-size:min(100%, 12ch-18ch)`
  and choose a `clamp()` max from the actual column width.
- Do not place large headings and right-side panels with negative margins,
  absolute positioning, or oversized transforms unless both elements have a
  tested width/height budget.
- Keep footer/source notes outside the main collision area. An absolute source
  note must have reserved bottom padding in `.slide-content`.

### Diagram/SVG Reliability

Prefer HTML/CSS diagrams, simple boxes, lines, and labels over elaborate inline
SVG. Inline SVG is allowed only for simple, deterministic diagrams.

For every inline SVG:

- Add explicit presentation attributes on SVG primitives instead of relying only
  on CSS classes. Open paths used as connectors must include `fill="none"`.
- Give connector paths a real fallback stroke, such as
  `stroke="currentColor"`, plus `stroke-width`, `stroke-linecap`, and
  `stroke-linejoin`.
- Avoid filters, masks, blend modes, `foreignObject`, huge paths, and unlabeled
  decorative blobs. These are frequent causes of black fills, clipping, or slow
  previews.
- Do not animate or assign `data-magic-id` to decorative SVG paths. Use Magic
  Move on labels, cards, numbers, or meaningful diagram nodes instead.
- If an SVG route, connector, arc, or edge renders as a black filled shape,
  the slide is broken. Add `fill="none"` to the source path and regenerate.

Choose the deck's background and theme system before scaling the deck. Do not
drop isolated inverse-theme pages into the middle of the deck just by inverting
the normal content template: light pages in a mostly dark deck are just as
disruptive as dark pages in a mostly light deck. Contrast pages are allowed
when they are special display moments: chapter breaks, full-bleed visual beats,
quote/manifesto pauses, warning/risk interrupts, or deliberate dramatic
reveals. They should differ in role and composition from ordinary evidence
slides, and neighboring slides should make the shift feel intentional. A
30-slide deck should not have one-off theme reversals that read as accidental
copies of the same layout with a different background.

Avoid repeated visible skeletons. In a 30-slide deck:

- No single layout signature should dominate.
- `title + three cards` should be rare and justified.
- `image left + text right` should vary by crop, hierarchy, or purpose.
- Chips and badges should act as navigation, status, grouping, or data labels,
  not decoration.
- If three consecutive slides share the same title block, accent line, grid, and
  card treatment, rewrite one before continuing.

## Text Fit

Clipped text is a broken slide.

Rules:

- Use `min-width:0` on flex/grid children that contain text.
- For wrapping text, use `max-inline-size`, line-height, and
  `overflow-wrap:break-word`.
- For one-line text, allocate a container width first, then choose a `clamp()`
  maximum that fits that width.
- For large values inside cards or panels, consider `container-type:inline-size`
  and `cqw` units so type scales from the container.
- Never use `overflow:hidden` to hide excess text. If a glyph, digit, unit, or
  punctuation mark is cropped, redesign the slide.

## Required Slide Structure

Each slide file contains only one section:

```html
<section class="slide" data-id="unique-id" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content">
    <!-- content -->
  </div>
</section>
```

Required:

- Root element is `<section class="slide">`, not `<div>`.
- Attributes: `data-id`, `data-transition`, `data-stagger`, `data-bg`.
- `.slide-content` wrapper is present.
- File names are `slide-01.html`, `slide-02.html`, etc.
- No DOCTYPE, `html`, `head`, `body`, or script tags in slide fragments.

## Style System

`style.css` should implement Brief Lite, not a generic template.

Include:

- `:root` variables for motion, core colors, typography, and reusable spacing.
- Base slide and `.slide-content` layout.
- Typography hierarchy.
- The deck-specific components actually needed by the story.
- Motion keyframes used by slide transitions and non-Magic Move entrances.
- Responsive text and container rules.

Avoid:

- Building many classes to prove complexity.
- Recoloring the same card under many names.
- Making every block glow or every heading use the accent.
- Using background effects as a substitute for composition.
- Creating visual components that do not correspond to story roles.

Good components are semantic: timeline, source note, comparison, risk map,
teardown, image frame, data strip, chapter rail, quote, decision map, or another
role that belongs to the deck.

## Images

Read `references/images.md` before generating or placing images.

## File Hygiene

Keep the topic root reserved for final deliverables:

- `{topic}/index.html`
- `{topic}/assets/` when assets are used
- `{topic}/sources/`

All process artifacts belong inside `{topic}/sources/`, including
`outline.md`, optional helper scripts such as `create_sources.mjs`, QA
screenshots/reports, drafts, and notes. Do not leave process files in the topic
root.

General rules:

- Generate images before writing slides that reference them.
- Every generated image must be used.
- If the user requested images, at least the planned visual anchor slides must
  contain rendered images unless the user approved a no-image fallback.
- Use descriptive English filenames.
- Use `../assets/...` from slide fragments under `sources/`; the merge script
  normalizes these to `./assets/...` in the final `index.html`.
- All content images should use the uploadable image wrapper required by
  `images.md`.
- Background images are reserved for cover or closing slides unless the user
  explicitly requests otherwise.
- Middle slides should use content images, diagrams, or CSS composition rather
  than full background images.

## Magic Move Strategy

Before coding all slides, map adjacent slide pairs.

Prefer shared elements that are genuinely semantic:

- Deck title or section label.
- Agenda item becoming a section heading.
- Card title, chip, metric label, or key number.
- Reused image with a changed crop or scale.
- Stable panel or diagram element.

Rules:

- Text elements with `data-magic-id` must have `display:inline-block`.
- Visible text must be identical across the shared elements.
- Use the smallest stable child when the whole block changes.
- Do not use `data-magic-id` on decorative lines, empty divs, backgrounds, or
  fake duplicates.
- For decks longer than 12 slides, most adjacent pairs should have at least one
  meaningful shared anchor unless there is a hard chapter break. A 30-slide
  Magic Slide deck should normally be planned as continuous chains of deck
  labels, section labels, lens chips, metrics, images, or concepts, not as 30
  isolated pages.

Before full generation, write a compact continuity map. It can be informal, but
it must cover every adjacent pair: `1->2 deck title/lens chips`, `2->3 section
label`, `3->4 none: hard chapter break`, and so on. Use this map while writing
the HTML, then verify the actual IDs after generation.

## Objective QA

After generating the full deck:

- Read beginning, middle, and end slide fragments.
- Check all slides use the required structure and file names.
- Check Magic Move ids are genuine and adjacent where intended.
- Merge slides with `merge-slides.py`.
- Inject runtime with `inject-runtime.py`.
- Preview with `serve.py`.
- Run browser or manual viewport checks on every slide at a normal 16:9 viewport
  and a smaller 16:9 viewport, such as `1440x900` and `1024x576`.
- Check for overflow, clipped text, broken images, dead zones, unbalanced
  columns, and runtime fit issues.
- If any slide receives `.ms-fit-scale` or `.ms-fit-top`, treat it as a layout
  failure and revise the source slide. Runtime fit is an alarm, not a pass.
- If images were requested, verify the final deck has actual assets and rendered
  image slides.
- Inspect rendered screenshots from at least six roles: cover, early evidence,
  image/diagram, dense middle, risk/summary, and closing.
- Do a design director pass: name the three roughest or most generic rendered
  slides, then revise them. If fewer than three are weak, explicitly say why the
  remaining candidates are acceptable.

Subjective design review remains visual and qualitative. Ask whether the deck
still feels specific, memorable, and coherent after the full build. If not,
revise the style contract, CSS, and weakest source slides instead of making
small cosmetic patches.

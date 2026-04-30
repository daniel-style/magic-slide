# Layout Guidelines — Slide Structure

This document defines the standard layout patterns for Magic Slide presentations to ensure consistency and usability.

## Core Layout Principle

**Every slide must be readable, well-structured, and fit within one viewport.** No scrolling, no overflow. Creative aesthetics should enhance, not break, the fundamental layout.

## Layout Primitive Policy

To keep generation reliable, **every slide must choose exactly one primary layout primitive before any HTML is written.**

Approved primary primitives:
- Cover
- Section Header
- Text + List
- Metrics/Grid
- Single Visual
- Horizontal Split
- Timeline
- Comparison
- Quote
- Diagram / Teardown
- Risk / Decision Map

Rules:
- **One slide = one primary primitive.** Do not hybridize two root layouts on the same slide.
- Keep structural depth shallow: `.slide-content` -> one primary layout container -> content blocks.
- Let visual creativity happen in typography, color, texture, and motion, not in improvised container geometry.
- If content does not fit cleanly inside one primitive, **split the slide** instead of inventing a new layout on the fly.

### Content Density And Finish

**Each slide MUST fit within one viewport (100vh), but fitting is not the same
as feeling finished.**

Use one primary primitive, then give it the right amount of supporting detail:

- A focal element: title, number, image, diagram, quote, or comparison.
- Supporting evidence: caption, source note, proportional bar, callout, label,
  sequence number, image crop, or short explanatory text.
- Enough negative space for hierarchy, but not so much that the slide feels
  abandoned.

Do not treat a fixed element count as a design goal. A slide with only a title
and one generic card is usually under-designed. A slide with many tiny items is
usually overloaded. If content does not fit cleanly inside one primitive, split
it into two slides rather than cramming.

### Framed Content Occupancy Rule

A visible frame, panel, card, or `visual-card` promises that the area inside it
contains a finished visual object. Do not use a large bordered container as
padding around a tiny row of nodes, chips, or cards. That reads as an empty
placeholder, not intentional negative space.

Rules:
- A framed main visual must either be tightly sized to its contents or have
  enough internal structure to feel complete: routes, lanes, annotations,
  legends, axes, callouts, nested regions, image/detail layers, or a deliberate
  art-directed composition.
- Do not give generic frame classes a large `min-height` and then reuse them
  for low-density content. `min-height`, aspect-ratio, and large padding belong
  on specific slide roles whose content actually fills that surface.
- If a system map has only two to four small nodes, prefer an unframed flow,
  a full-width row of individual cards, or a compact band. Add a parent frame
  only when the parent itself communicates something, such as a boundary,
  runtime, region, stage, or controlled environment.
- If most of the frame's interior is blank after rendering, fix the source:
  shrink the frame, expand the diagram, add meaningful supporting structure, or
  split the idea. Do not accept the empty area as "breathing room."
- Intentional negative space is allowed outside the primary object or inside a
  designed composition. It is not allowed as accidental dead space inside a
  bordered wrapper.

### Viewport Budget Rule

Before writing markup, count vertical zones:

- Title/kicker/subtitle counts as one zone.
- Main visual, list, comparison, diagram, or metric grid counts as one zone.
- Footer/source/caption rail counts as one zone.

Most slides should fit within two or three zones. A slide with a title zone,
two dense columns, a metric-card row, and a source note is already over budget.
Do not solve this with smaller type or `overflow:hidden`; split the content or
choose the single point that matters.

Reserve footer space when a source note is needed. A source note appended after
an already-full layout is a common cause of bottom clipping.

### Usable Width And Card Group Rule

Use the slide's available width before shrinking supporting cards. A common
failure is putting three or four text cards inside a narrow text column while
large blank areas remain on either side of the slide. That is a layout failure,
even when the cards technically fit.

Rules:
- The base `.slide-content` should give ordinary slides a wide 16:9 content
  budget. Avoid a narrow centered content column unless the primitive is
  intentionally editorial text.
- Multi-card rows, phase boxes, comparison cells, and small evidence cards need
  a real minimum inline size. As a rule of thumb, body-text cards should not
  drop below `14rem` or about `16ch` of readable text width.
- If a row of cards would become narrower than its text budget, let the group
  span the full primary layout width, move it below the split as a full-width
  evidence band, reduce the number of cards, or split the slide.
- Do not place a three-card evidence row under a right-column paragraph while
  the left side or outer slide margins are empty. Reallocate that horizontal
  space to the card group.
- In a horizontal split, a single column may contain at most two paragraph or
  metric cards unless each card has a proven minimum text measure of `16ch`.
  Three or more cards belong in a full-width evidence band, a separate
  Metrics/Grid slide, or a second slide.
- Never place four or five metric cards inside one half-width column. This
  causes long labels such as customer names, retention labels, and attach-rate
  labels to collide even when viewport-bound checks pass.
- For metric cards whose value is a word or phrase rather than a short number,
  treat the value as a heading: allow wrapping, lower the minimum font size,
  or use a wider card. Do not use a large non-wrapping metric style for words
  like `Customers`, `Retention`, or `Attach Rate` in narrow cards.
- Prefer `grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr))`
  for variable card groups, and use larger minima such as `16rem`-`18rem` when
  cards contain paragraphs.
- Use `min-width:0`, `container-type:inline-size`, `max-inline-size:100%`, and
  `overflow-wrap:break-word` on card contents so long words wrap inside the
  intended card instead of escaping or forcing overflow.

### Vertical Balance Rule

Most slides should have their primary content group around the optical center
of the viewport. This applies to ordinary business-report, evidence, metrics,
image+text, comparison, quote, and diagram slides. A slide feels broken when its
main group sits in the upper third with a large unused area below, even if
nothing technically overflows.

Rules:
- Default to centered `.slide-content`; do not use `.slide-dense`,
  `.slide-top`, or `justify-content:flex-start` for ordinary slides.
- Hard gate: do not add `.slide-top`, `.slide-dense`, or
  `justify-content:flex-start` unless the main content group occupies at least
  about 70% of the usable slide height or the slide contains a genuinely dense
  table/matrix/timeline/diagram that would otherwise collide with the top
  navigation. A title, subtitle, compact table, card row, and source note do
  not satisfy this gate.
- A source note, footer, slide counter, or small caption does not make a slide
  dense. Reserve footer space, but keep the primary group centered in the
  remaining visual field.
- Do not put source notes in the same centered flex column with
  `margin-top:auto`; that pushes the primary content group upward and creates a
  false "balanced" layout. Prefer an absolutely positioned `.source` anchored
  near the bottom of `.slide-content`, or wrap the main content in a `.stage`
  that stays centered while the source note sits outside the centering flow.
- Top alignment is allowed only when the main content truly needs it because it
  fills most of the viewport: dense tables, multi-row matrices, long timelines,
  or complex diagrams. If the content group occupies less than roughly two
  thirds of the usable height, top alignment is almost always wrong.
- If a rendered slide has a large empty region below the main content group,
  remove the top-aligned class or enlarge/rebalance the primitive. Do not leave
  ordinary evidence, scorecard, KPI, or comparison slides stranded in the upper
  third.
- Keep `.slide-content` vertically centered and let the main `.stage` or
  primitive container be the centered child.
- If a slide needs a very small visual, either enlarge the visual intentionally
  or tighten the content group; do not leave a large accidental dead zone below
  it.
- Runtime may add `.ms-sparse-balance` to repair accidental top alignment, but
  source slides should still be authored centered. Runtime classes
  `.ms-fit-top` and `.ms-fit-scale` are warnings; revise the source layout
  instead of accepting a top-shifted or scaled sparse slide.

### Repetition Rule

Reliability does not mean repeating one visual formula. In a 30-slide deck:
- No single primitive should dominate the deck.
- Metrics/Grid is a support primitive, not the default slide shape.
- A repeated primitive must change hierarchy, crop, density, or purpose enough
  that the deck still feels composed.
- If three consecutive slides have the same visible skeleton, rewrite one of
  them with a different primitive.

## Responsive Font Scaling

Responsive type must respect the content budget. Do not stack an aggressively
scaling `html` font size with large `vw`-based font sizes on every child; this
makes dense slides overflow at normal 16:9 sizes.

Use viewport scaling for true hero/display moments, and use rem or
container-relative sizing for dense slide content, cards, captions, and labels.

### Required CSS in style.css

```css
/* Modest responsive font scaling base */
html {
  font-size: clamp(14px, 1vw, 18px);
}

/* Optional scale token for hero/display moments */
:root {
  --font-scale: clamp(0.9, 1vw, 1.15);
}
```

### Font Size Guidelines

**Use relative units (rem) instead of fixed px:**

```css
/* ❌ WRONG: Fixed pixel sizes */
h1 { font-size: 48px; }
p { font-size: 16px; }

/* ✅ CORRECT: Responsive rem sizes */
h1 { font-size: 3rem; }  /* Scales with html font-size */
p { font-size: 1.2rem; }

/* ✅ BETTER FOR HERO/DISPLAY: Viewport-based with clamp */
h1 { font-size: clamp(2.5rem, 5vw, 5rem); }
p { font-size: clamp(1rem, 1.15vw, 1.3rem); }
```

### Recommended Responsive Sizes

**For inline styles in HTML:**

```html
<!-- Cover slide title -->
<h1 style="font-size: clamp(3rem, 6vw, 6rem);">Title</h1>

<!-- Section title -->
<h2 style="font-size: clamp(2rem, 4vw, 4rem);">Section</h2>

<!-- Slide title -->
<h2 style="font-size: clamp(1.8rem, 3vw, 3.5rem);">Slide Title</h2>

<!-- Body text for dense or normal slides -->
<p style="font-size: clamp(1rem, 1.15vw, 1.3rem);">Content</p>

<!-- Small text -->
<p style="font-size: clamp(0.78rem, 0.9vw, 0.95rem);">Caption</p>
```

**Why clamp():**
- `clamp(min, preferred, max)` can keep text readable across screen sizes.
- The `max` value must be chosen from the container width and slide height
  budget, not from visual ambition alone.
- For card values, prefer container-relative `cqw` sizing over viewport sizing
  so one large number does not force the whole slide to overflow.

## Standard Slide Structure

```html
<section class="slide" data-id="..." data-transition="..." data-stagger="..." data-bg="...">
  <div class="slide-content">
    <!-- Content goes here -->
  </div>
</section>
```

## Required CSS for .slide-content

**In style.css, ALWAYS include a neutral base that vertically centers ordinary
slides:**

```css
.slide-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  width: 100%;
  max-width: 1680px;
  margin: 0 auto;
  padding: clamp(2.5rem, 5vw, 5rem);
  min-height: 100vh;
  box-sizing: border-box;
}

.slide-center .slide-content {
  align-items: center;
  text-align: center;
}

.slide-top .slide-content,
.slide-dense .slide-content {
  justify-content: flex-start;
}

.source {
  position: absolute;
  left: clamp(2.5rem, 5vw, 5rem);
  right: clamp(2.5rem, 5vw, 5rem);
  bottom: clamp(1.8rem, 3vw, 3rem);
}
```

**Why these properties matter:**
- `display: flex` — Enables flexible layout
- `flex-direction: column` — Stack content vertically
- `justify-content: center` — Centers ordinary slides by default; only truly
  dense slides may override to `flex-start`
- `align-items: stretch` — Gives each primitive a predictable width budget
- `max-width: 1680px` — Uses a wide 16:9 content budget without letting text
  become unmanageably long
- `min-height: 100vh` — Fill viewport height
- `padding: 4rem` — Breathing room on all sides
- Evidence, comparison, metrics, image+text, and source-noted slides should
  remain centered unless their main content fills most of the viewport. Use a
  top-aligned variant such as `.slide-dense` only for genuinely dense tables,
  large matrices, long timelines, or complex diagrams with an explicit reason.

## Slide Type Patterns

For detailed HTML structure and examples of each layout primitive, see [layouts/primitives.md](layouts/primitives.md).

**Available primitives:**
- Cover Slide (Title Slide)
- Section Header Slide
- Content Slide (Text + List)
- Metrics/Grid Slide
- Single Visual Slide
- Horizontal Split Slide
- Timeline Slide
- Comparison Slide
- Quote Slide
- Diagram / Teardown Slide
- Risk / Decision Map Slide

## Typography Scale

**Recommended responsive font sizes using clamp():**

```css
/* Cover slide */
H1: clamp(3rem, 6vw, 6rem)

/* Section headers */
H2 (section): clamp(2rem, 4vw, 4rem)

/* Slide titles */
H2 (slide): clamp(1.8rem, 3vw, 3.5rem)
H3 (subsection): clamp(1.5rem, 2.5vw, 2.5rem)

/* Body text */
Body: clamp(1rem, 1.15vw, 1.3rem)
Small: clamp(0.78rem, 0.9vw, 0.95rem)
```

**Line height:**
- Headings: 1.2
- Body text: 1.6-2

**Spacing (also responsive):**
- Between title and content: clamp(1.5rem, 3vw, 3rem)
- Between paragraphs: clamp(0.8rem, 1.5vw, 1.5rem)
- Between list items: clamp(0.5rem, 1vw, 1rem)

## Text Fit and Non-Wrapping Tokens

Every rendered text box must be fully visible inside its intended container. This is a general layout rule, not a runtime rescue path. It applies to headings, labels, captions, buttons, metric values, dates, names, and any other text.

Non-wrapping tokens are high-risk because a single string can be wider than its card. Treat them as objects with a width budget.

**Safer pattern for large numeric callouts:**

```html
<div class="card" style="width:min(46vw,700px); min-width:0; container-type:inline-size; padding:clamp(1.5rem,3vw,3rem); overflow:visible;">
  <span class="stat-value" style="display:inline-block; max-inline-size:100%; font-size:clamp(2.75rem,18cqw,6.5rem); line-height:.9; white-space:nowrap;">
    $215.9B
  </span>
  <p class="stat-label" style="max-inline-size:100%; overflow-wrap:break-word;">
    FY2026 revenue, up 65% year over year.
  </p>
</div>
```

Rules:
- Before choosing a font size, decide the container width budget and the longest likely text string.
- Prefer container-relative sizing for text inside cards: set `container-type:inline-size` on the card and use `cqw` inside `clamp()`.
- Text cards with paragraph copy need enough inline space to breathe. If a
  card's usable text measure falls below roughly `16ch`, widen the card, let
  the card group use more of the slide, or split the content.
- Use `white-space:nowrap` only when the full token fits. Otherwise reduce the max font size, widen the container, or allow wrapping.
- Use `min-width:0` on grid/flex children and `max-inline-size:100%` on text blocks so parent constraints actually work.
- In multi-column layouts, large headings must also be capped by the column width, such as `max-inline-size:min(100%, 18ch)`. A heading with `18ch` alone can still overflow a narrow grid track and cover the neighboring panel.
- Never rely on `overflow:hidden` to crop text. If any glyph, digit, punctuation, or unit suffix is hidden, the layout is broken.
- If the text plus its supporting label cannot fit with comfortable padding, enlarge the container, move the focal text outside the card, or split the slide.

## Collision And Overlap Guardrails

Large headings in split layouts are the most common cause of visual collisions.
Treat every heading, diagram, card group, and source note as a box with a real
width and height budget.

Rules:
- In two-column or diagram layouts, cap display headings by the actual column
  width: `max-inline-size:min(100%, 12ch)` to `min(100%, 18ch)` depending on
  the line count.
- If a heading becomes more than four display lines, reduce the max `clamp()`,
  widen the text column, or split the idea into another slide.
- Use `grid-template-columns:minmax(0, ...) minmax(0, ...)` and `min-width:0`
  on both columns so text cannot escape its track.
- Avoid negative margins, oversized transforms, and absolute positioning for
  primary content. Use absolute positioning only for background rails, chapter
  marks, source notes, or small decorative elements with reserved space.
- Source notes placed with `position:absolute` require reserved bottom padding
  in `.slide-content`; otherwise the last content row can collide with them.
- Do not rely on `overflow:hidden` to hide a collision. Hidden overlap is still
  a broken slide.

### Cover Text Safety Zone

Cover decoration is only successful when it frames the title block instead of
competing with it. A cover with route lines, dots, traces, or pseudo-diagrams
crossing the hero copy is a readability failure even if every element fits.

Rules:
- Before placing decorative lines, particles, nodes, grids, SVG traces, or
  pseudo-elements on a cover, define a quiet text safety zone around the title,
  subtitle, logo/wordmark, and chip or CTA row.
- High-contrast decoration must not pass through, touch, underline, or visually
  slice through cover text. Keep it outside the safety zone by at least
  `clamp(1.5rem, 3vw, 4rem)`.
- If a background treatment sits behind text, it must be low-contrast and
  non-directional: grain, soft texture, or a broad material wash. Do not put
  linework, routes, arrows, nodes, or sharp geometric marks behind letterforms.
- Use at most one decorative system on a cover, such as a material field,
  faint grid, route motif, or particle map. If the title needs a panel or fog
  overlay to stay readable, remove or move the decoration instead.
- Inspect the cover at full slide size and in overview thumbnail size. If the
  decoration is noticed before the title or makes the subtitle harder to read,
  move it to the edges/corners, lower its contrast, or delete it.

## Common Layout Mistakes

### ❌ WRONG: Empty left, crowded right (horizontal split)
```html
<div class="slide-content" style="flex-direction: row;">
  <div style="flex: 1;"></div>  <!-- Empty left side -->
  <div style="flex: 1;">
    <h2>Title</h2>
    <p>All content crammed on right side</p>
  </div>
</div>
```
**Problem:** One side is empty, creating unbalanced layout. Use vertical stack instead, or put image on the empty side.

### ❌ WRONG: Three cards squeezed inside one narrow column
```html
<div class="split" style="display:grid; grid-template-columns:1fr 1fr; gap:4rem;">
  <figure><!-- small image --></figure>
  <div>
    <h2>Services deepen the base.</h2>
    <p>Short explanation.</p>
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:.75rem;">
      <article class="card">Distribution...</article>
      <article class="card">Utility...</article>
      <article class="card">Financial cadence...</article>
    </div>
  </div>
</div>
```
**Problem:** The cards inherit only the right column's width while the slide's
outer width stays unused, so body text wraps every word and may overflow.

### ✅ CORRECT: Card row gets a full-width evidence band
```html
<div class="stage" style="display:grid; gap:clamp(1.5rem,3vw,3rem);">
  <div style="display:grid; grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr); gap:clamp(2rem,4vw,4rem); align-items:center;">
    <figure style="min-width:0;"><!-- image --></figure>
    <div style="min-width:0;">
      <h2 style="max-inline-size:min(100%,14ch);">Services deepen the base.</h2>
      <p style="max-inline-size:42rem;">Short explanation.</p>
    </div>
  </div>
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,16rem),1fr)); gap:clamp(1rem,2vw,1.5rem);">
    <article class="card" style="min-width:0; container-type:inline-size;">Distribution...</article>
    <article class="card" style="min-width:0; container-type:inline-size;">Utility...</article>
    <article class="card" style="min-width:0; container-type:inline-size;">Financial cadence...</article>
  </div>
</div>
```
**Why:** The image/text split stays balanced, and the supporting cards use the
available horizontal space instead of becoming narrow columns.

### ❌ WRONG: Large empty frame around a tiny flow
```html
<div class="visual-card" style="min-height:24rem;">
  <div class="pipeline" style="display:grid; grid-template-columns:repeat(3,1fr);">
    <div class="node">Client</div>
    <div class="node">Gateway</div>
    <div class="node">Models</div>
  </div>
</div>
```
**Problem:** The frame is much larger than the actual flow, so the empty
interior looks like missing content. Shrink the wrapper, remove the wrapper, or
turn the flow into a complete diagram with lanes, routes, labels, and callouts.

### ✅ CORRECT: Compact flow without a fake stage
```html
<div class="stage" style="display:grid; gap:clamp(1.5rem,3vw,2.5rem);">
  <div><!-- heading and lead copy --></div>
  <div class="pipeline" style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:clamp(1rem,2vw,1.5rem);">
    <article class="card">Client</article>
    <article class="card">Gateway</article>
    <article class="card">Models</article>
  </div>
</div>
```
**Why:** The content itself carries the structure. There is no oversized parent
box implying a larger visual that never arrives.

### ❌ WRONG: No structure
```html
<section class="slide" data-id="bad" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <h1>Title</h1>
  <p>Text</p>
</section>
```
**Problem:** Missing `.slide-content` wrapper

### ❌ WRONG: Absolute positioning chaos
```html
<div class="slide-content">
  <h1 style="position: absolute; top: 10%; left: 20%;">Title</h1>
  <p style="position: absolute; top: 50%; left: 30%;">Text</p>
</div>
```
**Problem:** Absolute positioning breaks responsive layout and centering

### ❌ WRONG: Tiny fonts
```html
<h2 style="font-size: 0.8rem;">Title</h2>
<p style="font-size: 0.6rem;">Text</p>
```
**Problem:** Unreadable on projectors/large screens

### ❌ WRONG: Fixed pixel sizes
```html
<h1 style="font-size: 48px;">Title</h1>
<p style="font-size: 16px;">Text</p>
```
**Problem:** Doesn't scale with screen size, too small on large displays

### ❌ WRONG: No max-width on text
```html
<p style="font-size: 1.5rem; width: 100%;">
  Very long text that stretches across the entire screen making it hard to read...
</p>
```
**Problem:** Text too wide, hard to read

### ❌ WRONG: Huge metric clipped by its card
```html
<div class="card" style="width:520px; overflow:hidden;">
  <div style="font-size:8rem; white-space:nowrap;">$215.9B</div>
</div>
```
**Problem:** The card can hide the right side of the number. Users must see the full value.

### ✅ CORRECT: Container-sized metric token
```html
<div class="card" style="width:min(46vw,700px); min-width:0; container-type:inline-size; padding:clamp(1.5rem,3vw,3rem); overflow:visible;">
  <span class="stat-value" style="display:inline-block; max-inline-size:100%; font-size:clamp(2.75rem,18cqw,6.5rem); line-height:.9; white-space:nowrap;">
    $215.9B
  </span>
</div>
```
**Why:** The authoring CSS sizes the token from the card width, so the value is designed to fit before the deck reaches the runtime.

### ✅ CORRECT: Structured layout with responsive fonts
```html
<section class="slide" data-id="good" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content">
    <h2 style="font-size: clamp(1.8rem, 3vw, 3.5rem); margin-bottom: clamp(1.5rem, 3vw, 3rem); align-self: flex-start;">
      Title
    </h2>
    <p style="font-size: clamp(1rem, 1.15vw, 1.3rem); line-height: 1.7; max-width: 800px;">
      Readable text with proper sizing and width constraint that scales with viewport.
    </p>
  </div>
</section>
```

## Aesthetic Variations

**You can customize aesthetics while maintaining structure:**

### Minimal & Refined
- Generous whitespace (padding: 6rem)
- Subtle colors
- Clean typography

### Bold & Dramatic
- Dark backgrounds
- Electric accent colors
- Dramatic shadows

### Playful & Creative
- Bright colors
- Slight rotations (transform: rotate(-2deg))
- Bouncy animations

**BUT:** Always keep the core `.slide-content` structure intact.

## Checklist

Before generating, ensure:
- [ ] Each slide can be described as exactly one approved primary primitive
- [ ] Every slide has `.slide-content` wrapper
- [ ] `.slide-content` has proper CSS (flex, max-width, padding) and dense
      slides override vertical centering
- [ ] Font sizes are chosen from the slide budget; use clamp() or cqw only where
      it helps fit and legibility
- [ ] Minimum readable body size is about 1rem; avoid pushing dense body copy
      toward hero-scale sizes
- [ ] Text has max-width constraints (700-900px)
- [ ] Every text element is fully visible inside its intended container; non-wrapping tokens have an explicit width budget
- [ ] Multi-card rows use the available slide width; no paragraph card is
      squeezed below roughly `16ch` while nearby horizontal space is empty
- [ ] Framed main visuals have real internal occupancy; no oversized bordered
      wrapper surrounds a tiny row, sparse chips, or a low-density mini-flow
- [ ] Spacing uses clamp() for responsive gaps
- [ ] No absolute positioning chaos
- [ ] Layout works at different screen sizes
- [ ] **Horizontal splits have content on BOTH sides** (no empty columns)
- [ ] **Image + text layouts use proper flex structure** (45% image, 55% text with gap)
- [ ] **No slide contains a large accidental dead zone caused by wrapper sizing rather than intentional composition**

## Remember

**Creativity enhances structure, it doesn't replace it.**

A beautiful, distinctive presentation is still useless if the content is unreadable or the layout is broken.

# HTML Contract — Core Rules

These are the non-negotiable rules for generating slide HTML.

## Slide Structure

**Root element:**
- MUST be `<section class="slide">`, NEVER `<div class="slide">`
- This is the #1 most common error — the FLIP engine requires `<section>`

**Required attributes on every slide:**
```html
<section class="slide" 
         data-id="unique-id" 
         data-transition="fade" 
         data-stagger="cascade" 
         data-bg="dark">
```

- `data-id` — Unique identifier (e.g., "cover", "overview-1", "detail-models")
- `data-transition` — Animation: "fade", "rise", "scale-in", "slide-up"
- `data-stagger` — Stagger mode: "cascade", "zoom-in", "fade-in", "fade-in-left", "fade-in-right", or "fade-in-down"
- `data-bg` — Perceived background tone: "dark", "light", "white", or a
  specific treatment such as "gradient-abstract". Use "light" or "white" for
  bright/paper/canvas fields and "dark" for dark fields.

**Stagger default:** Every ordinary slide should use a real stagger mode.
Do not generate `data-stagger="none"` as a convenience default. The injector
normalizes accidental `none` values to `cascade` so decks keep their entrance
motion. Only disable a whole slide's stagger when the user explicitly asks for
no entrance animation, and mark that intent with
`data-stagger-disabled="true" data-stagger="none"`.

**Stagger target rule:** Headings, paragraphs, captions, and lead copy should
stagger as whole block elements. They may contain inline spans for language
variants, emphasis, or short styling hooks, but do not rely on ordinary inline
spans as stagger targets because CSS transforms do not apply reliably to inline
text. Large text blocks must have a visibly delayed entrance, not just a class
name; the runtime treats them as `.ms-stagger-text` with a stronger rise so the
first headline is still perceptible.

**File structure:**
- Each slide file contains ONLY a `<section>` element
- No DOCTYPE, `<html>`, `<head>`, `<body>` tags
- File naming: `slide-01.html`, `slide-02.html`, ... (zero-padded two digits)

**Direct child discipline:**
- The ordinary content wrapper must be the only non-background direct child:
  `<div class="slide-content">...</div>`.
- Full-bleed decorative/background layers may be direct children only when they
  use class `.bg`, are `aria-hidden="true"`, and sit behind `.slide-content`.
- Do not put brand marks, page numbers, section counters, labels, or other
  visible slide chrome as direct children of `.slide`. Put necessary marks
  inside `.slide-content` or omit them.

## Layout Contract

These rules are non-negotiable because unconstrained HTML/CSS generation is the fastest way to get broken layouts.

1. **Every slide must map to one approved primary layout primitive** from `layout-guide.md`
2. **Do not hybridize root layouts** on one slide just because the content feels ambitious
3. Keep structural depth shallow: `.slide-content` -> one primary layout container -> content blocks
4. If a slide cannot stay clean within one primitive, split it into two slides
5. Prefer stable, proven layout patterns over one-off structural inventions

## Background Contract

Every slide's main background must be owned by the root `.slide` element and
must cover the entire viewport, including wide or ultra-wide browser windows.
Do not make the apparent background an inset `.slide-content`, `.stage`, card,
panel, pseudo-frame, or centered rectangle.

Rules:
- Set `background`, `background-size`, `background-position`, and theme variants
  on `.slide` or `.slide[data-bg="..."]`.
- Decorative full-bleed texture may use `.slide::before` / `.slide::after` with
  `position:absolute; inset:0; pointer-events:none`.
- `.slide-content` is a layout wrapper only. It may constrain content width, but
  it must not create the visible page boundary.
- A full-bleed decorative/image layer must be either the root `.slide`
  background or a direct child of `.slide`, outside `.slide-content`, such as:
  `<div class="bg cover-bg" aria-hidden="true"></div>`. Use
  `position:absolute; inset:0; background-size:cover; background-position:center`.
- Never place a full-bleed-looking layer inside `.slide-content`. This fails on
  wide screens because `.slide-content` often has `max-width` and `margin:auto`;
  `.slide-content > .cover-image { position:absolute; inset:0; ... }` is an
  explicit anti-pattern.
- If a theme uses a paper, blueprint, canvas, photo, gradient, or color wash, it
  must visibly reach all four slide edges in both single-slide view and overview
  thumbnails.
- Do not use body background or overview-item fallback color as a substitute for
  a real slide background.

## Slide Chrome Contract

Generated source must not create UI that looks like browser chrome, a preview
toolbar, or a broken runtime control. The runtime already owns navigation,
progress, counters, edit controls, and the preview toolbar.

Rules:
- Do not generate long, thin rounded bars near the top edge, fake address bars,
  browser-toolbar strips, full-width brand pills, or top rails with a small
  brand name inside. These read as bugs in rendered decks.
- Do not create repeated per-slide `brand-mark` / `section-no` chrome as direct
  children of `.slide`. If a brand or section cue is genuinely useful, make it
  a small text mark inside the slide's composition, source/caption area, or a
  real heading/kicker with enough surrounding context.
- Repeated brand/page marks must not be used as `data-magic-id` anchors. They
  are presentation chrome, not content relay.
- Keep ordinary content away from the extreme top runtime-control zone unless
  the slide is a deliberate dense table/timeline and has reserved space.

## Deck Tone Mode Contract

Every deck must choose one primary tone mode before slide HTML is written:
`primary-tone: dark` or `primary-tone: light`.

Rules:
- The primary tone applies to the cover and all ordinary content slides by
  default. Do not alternate dark and light slides just to add variety.
- If no inverse-tone exceptions are named in Brief Lite or the internal
  production plan, every slide's root background and `data-bg` must follow the
  primary tone.
- Inverse-tone slides are allowed only as named exceptions with a story role:
  cover/opening display, chapter break, quote/manifesto pause, warning/risk
  interrupt, full-bleed visual beat, product/object reveal, or closing display
  moment.
- An inverse-tone exception must be visibly different in composition from
  ordinary evidence slides. A normal card/list/table slide with swapped colors
  reads as accidental and must be converted back to the primary tone.
- Neighboring slides must make the tone shift feel intentional through title,
  transition, chapter marker, Magic Move continuity, or another clear cue.
- `data-bg` must describe the rendered tone of the root `.slide`, not the body
  fallback or an inset panel. Overview thumbnails are part of the check.

## Cover Contract

Slide 1 must be a true cover, not an ordinary content slide wearing a title.

Rules:
- `slide-01.html` must use a dedicated cover/display composition.
- The cover must be visually distinct from slide 2 in layout skeleton, scale,
  density, and focal element.
- The cover H1 must be concise enough to read like a poster title, not a
  descriptive sentence. Default to 1-5 English words or 2-12 CJK characters,
  and keep it to at most two lines at the final display size.
- Distill long topic phrases into a short cover title, then move qualifiers to
  a terse subtitle, small chips, or slide 2. For example, use `Agent
  Infrastructure` as the H1 instead of `Agent Infrastructure for Production AI
  Systems`.
- Cover subtitle copy is optional and must stay brief: one short clause, not a
  deck abstract, table of contents, or comma-separated inventory. Avoid copy
  such as `A 40-slide brief on...` on the cover.
- Default cover background is no-image. Use a premium minimalist CSS material
  field on the root `.slide`: restrained gradients, subtle pattern or texture,
  strong typography, and whitespace. It must read as grand, simple, and
  high-end in the first second.
- For company, product, AI, infrastructure, SaaS, and developer-tool decks, the
  default cover composition is the title/wordmark, one optional terse subtitle,
  at most 1-3 small labels/chips, and simple non-text decoration. Put
  architecture maps, process flows, feature cards, request diagrams, and
  explanatory mini-panels on slide 2 or later, not on the cover.
- Do not use a generated/photo cover background unless the user explicitly
  asked for cover imagery or the topic requires a recognizable product/place/
  object on slide 1.
- Avoid repeated cards, ordinary memo grids, dense tables, or the same
  two-column layout used in subsequent slides.
- The cover may share one semantic Magic Move element with slide 2, such as the
  title/wordmark when it is the main cover text, or one key phrase, but the rest
  of the composition should clearly change role after the opening.
- The cover should have one primary focal object: hero title, product/object
  image when explicitly justified, typographic crop, or strong material field.
  Do not make a labeled process diagram, row of nodes, or card flow the cover's
  focal object unless the user explicitly requested a diagram-first cover.
- If the user explicitly asks for a diagram-first cover, it must be symbolic
  and poster-like: no paragraphs inside nodes, no tiny labels, no pale cards
  with pale text, and no operational architecture that must be read to
  understand the title.
- Decorative cover layers must satisfy the Cover Text Safety Zone in
  `layout-guide.md`: no visible route, trace, dot, pseudo-element, or diagram
  mark may cut through the title, subtitle, wordmark, or chip row.
- Do not put `data-magic-id` on cover-only diagram nodes, flow cards, arrows, or
  decorative labels. Cover Magic Move should usually hand off only the main
  title/wordmark or one short key phrase into slide 2.
- If the cover uses a subject image, it must be full-bleed, a wide hero panel,
  a mostly visible product/object, or an abstract material field. Do not crop a
  landscape image into a tall skinny strip or arbitrary object sliver.
- Never implement the apparent cover background as an uploadable image wrapper,
  inset panel, document-flow image, or absolutely positioned child of
  `.slide-content`. Cover imagery, when explicitly allowed, must be owned by the
  root `.slide` background or a full-bleed absolutely positioned decorative
  layer that is a direct child of `.slide` behind `.slide-content`.

## Color Contrast Contract

The generated CSS must define a clean palette with usable contrast. Restrained
does not mean gray or muddy.

Rules:
- `:root` variables must include a dominant field (`--bg`), primary text
  (`--text`), secondary text (`--subtext`), and at least one purposeful accent
  (`--accent` or a clearly named equivalent such as `--blue`).
- Dark theme slides must keep their field clear: avoid broad white/gray
  translucent overlays that desaturate the whole slide into fog.
- Light, paper, canvas, blueprint, and pale-tint slides must use dark ink for
  headings and readable muted ink for secondary text. Do not use white, cream,
  pale-gray, or low-opacity text on a light field.
- Real content text must not depend on opacity below `0.72` or rgba/hsla alpha
  below `0.72` for hierarchy. Pick a legible color token instead.
- Accent blocks, badges, and route labels must use high-contrast foregrounds.
  Do not put dark same-hue text on a saturated blue/green/orange/red block.
- Neutral surfaces should be hue-tinted or material-specific. Generic gray
  panels on gray-blue/gray-green backgrounds are a palette failure unless the
  brief explicitly calls for austere monochrome.

## Text Fit Contract

All visible text must be readable in full. Do not allow a card, panel, button, column, or slide edge to crop headings, labels, numbers, units, captions, or punctuation.

Rules:
- Author the fit in CSS/HTML. Do not rely on runtime detection or hidden overflow to rescue text.
- Size card, panel, timeline, and grid-cell text from the container width, not
  only the viewport. Use `container-type:inline-size` on the component and
  `cqw` or a conservative `clamp()` for large labels.
- For wrapping text, use `max-inline-size`, appropriate `line-height`, and `overflow-wrap:break-word`.
- For non-wrapping text, first allocate a container width, then choose a font-size `clamp()` that fits that width.
- For card-contained text, prefer `container-type:inline-size` on the card and container query units (`cqw`) in the text size.
- Use `min-width:0` on flex/grid children containing text.
- For short Magic Move labels that must stay one line, use an approved label
  class or `data-magic-nowrap="true"` and give the element an explicit
  one-line width policy. Do not rely on the animated clone to discover a width
  during transition.
- Do not put three or more metric/text cards inside one half-width split
  column. Four-card and five-card groups must use the full slide width, a
  dedicated Metrics/Grid primitive, or multiple slides.
- Long word/phrase metric values must be sized like card headings, not like
  short numeric stats. They may wrap, use a lower minimum font size, or move
  into wider cards; they must never overlap adjacent cards.
- If the full text cannot fit, reduce the max font size, widen the container, allow wrapping, or split the slide.
- Do not hide text overflow with `overflow:hidden`, `overflow:clip`, masks, or
  fades. If content needs hiding to look tidy, the slide is over budget.
- In the QA overview longshot, first confirm iframe-loaded readiness, then
  visually inspect cards by slide number for escaped labels, cramped rows,
  unreadable wrapping/contrast, overlap, clipping, cropped media, and blank or
  unloaded cards. If `visual-issues.json` already has unresolved revision
  notes, repair those marked slides from JSON/source context first. Then use
  the rendered overview as verification, skipping marked cards during
  new-problem triage unless the repair still looks questionable.

## SVG Contract

Inline SVG is high-risk because a connector path without `fill="none"` can
render as a black filled shape if CSS is stripped, delayed, cloned, or scoped
differently by preview tools. Prefer HTML/CSS diagrams for simple system maps.
When SVG is used, make every primitive self-describing.

Rules:
- Every open `<path>` used as a route, connector, arrow, edge, trace, curve, or
  rail MUST include `fill="none"` directly on the element.
- Connector paths must also include fallback presentation attributes:
  `stroke="currentColor"`, `stroke-width`, `stroke-linecap="round"`, and
  `stroke-linejoin="round"`. CSS classes may override color and width.
- Do not rely only on CSS classes for `fill`, `stroke`, or `stroke-width`.
- Avoid `filter`, `mask`, `clipPath`, `foreignObject`, blend modes, huge freeform
  blobs, and decorative filled paths. These often cause black artifacts,
  clipping, or slow preview rendering.
- Do not put `data-magic-id` on decorative SVG paths. Use Magic Move on the
  diagram's labels, cards, nodes, or surrounding panels instead.

### SVG Visual Quality Contract

SVG diagrams must look like finished editorial or engineering graphics, not
placeholder wireframes. A diagram made of a few unstyled circles, default-thick
curves, and orphan labels is a failed slide even when the SVG is syntactically
valid.

Rules:
- Start with a named visual role: request lifecycle, routing map, protocol
  translator, audit trace, dependency stack, risk surface, or another concrete
  diagram type.
- Build at least three visible hierarchy layers: a quiet background field or
  grid, labelled nodes/cards, and purposeful routes/annotations. Do not leave a
  large plain rectangle containing only two or three shapes.
- Use restrained but intentional line rhythm: primary routes, secondary routes,
  node outlines, and evidence markers should have different weights, opacity,
  or color jobs.
- Align labels and nodes to an obvious grid. Avoid random floating labels,
  disconnected circles, and curves whose geometry does not explain the story.
- Prefer HTML labels/cards over SVG `<text>` when the labels need to remain
  editable, responsive, or Magic Move targets.
- If a simple diagram can only be expressed as "three circles connected by
  lines", replace it with a richer HTML/CSS system map or add real structure:
  lanes, stages, route types, state markers, legends, or evidence bands.
- Inspect rendered diagrams at slide size and thumbnail size. If it reads like
  a rough sketch or debug visualization, revise the source SVG before delivery.

## Brand And Logo Contract

For named companies, products, venues, or branded objects, do not invent a logo,
icon, monogram, prefix mark, or decorative pseudo-logo. A made-up stroke beside
a brand name is worse than no logo because it implies an official mark.

Rules:
- First look for an official logo/wordmark from the provided URL, page metadata,
  header image, favicon, documentation, or press/brand assets.
- If an official asset is available, use that asset for repeated deck marks or
  brand headers. Preserve its proportions and do not redraw it from memory.
- If no official asset is available, use a clean text-only brand label. Do not
  fabricate a symbol, partial icon, or decorative line that could be mistaken
  for a logo.
- If a drawn substitute is unavoidable, it must be explicitly derived from the
  verified official mark and should be treated as an approximation, not a new
  brand identity.
- Repeated slide marks should be official-logo or text-only. Avoid CSS
  pseudo-elements such as arbitrary strokes, hooks, brackets, or glyph fragments
  next to a brand name unless they are part of the verified identity.
- QA the cover plus at least one ordinary content slide. If the brand mark
  reads as a random fragment or unofficial logo, remove it or replace it with
  the official asset.

**Good SVG connector:**
```html
<path class="route-blue"
      d="M80 210 C350 210 350 82 448 82 H632"
      fill="none"
      stroke="currentColor"
      stroke-width="4"
      stroke-linecap="round"
      stroke-linejoin="round" />
```

## Magic Move Contract

Use `flip-engine.md` as the authority for `data-magic-id` planning and FLIP
runtime behavior. The HTML contract only verifies that Magic Move anchors are
used intentionally and do not appear on decorative-only elements. Normal-length
decks should expose a real continuity spine across adjacent slides; if most
transitions have no shared ids, revisit the outline or slide treatment rather
than adding decorative placeholders.

Do not add visible token rows, focus chips, magic labels, pills, badges, or
other body labels solely to manufacture Magic Move. A short label can carry
`data-magic-id` only when it is already necessary content, such as a real
status, timeline date, row label, card title, or diagram node label. If the
label would make the reader ask "what does this tag mean here?", remove the
magic-id or remove the label.

## Style Requirements

**style.css must include:**

1. **CSS Variables:**
```css
:root {
  --ms-dur: 600;
  --ms-ease: cubic-bezier(0.16, 1, 0.3, 1);
  --bg: [deck background];
  --text: [primary text];
  --subtext: [secondary text];
  --accent: [purposeful accent];
  --font-display: [style-specific display stack];
  --font-body: [readable body stack];
  --font-mono: [optional data/code/label stack];
}
```

2. **Animations:**
```css
@keyframes ms-rise {
  from { opacity: 0; transform: translateY(2rem); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes ms-scale-in {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes ms-slide-up {
  from { opacity: 0; transform: translateY(3rem); }
  to { opacity: 1; transform: translateY(0); }
}
```

3. **Base layout:**
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
```

Use `layout-guide.md` for centering, dense-slide exceptions, source-note
placement, design-canvas scaling, and overflow/collision policy.

## What NOT to Include

- No `<script>` blocks (runtime auto-injected)
- No progress bar, counter, navigation elements (auto-injected)
- No external CSS files (everything in style.css)
- No Lucide icons CDN (auto-injected)

## File Naming

- All file/folder names MUST be English only
- No CJK characters (prevents URL encoding issues)
- Zero-padded: slide-01.html, slide-02.html, ..., slide-10.html

## Common Mistakes

1. **Using `<div class="slide">` instead of `<section class="slide">`**
   - Fix: Change root element to `<section>`

2. **Using unreliable Magic Move anchors**
   - Fix: Apply the rules in `flip-engine.md`

3. **Missing required attributes**
   - Fix: Add data-id, data-transition, data-stagger, data-bg

4. **Creating class soup**
   - Fix: Use semantic deck-specific classes only when they describe real slide roles; otherwise use focused inline styles or existing simple classes.

5. **Clipping text inside a card or column**
   - Fix: author a real fit using container width, `min-width:0`, `max-inline-size`, wrapping, container query units, or a lower max `clamp()` value until the full text is visible

6. **Low-contrast text on a light surface**
   - Fix: use dark ink on light/paper fields and reserve white or cream text
     for dark surfaces only

7. **Random light/dark switching**
   - Fix: return ordinary slides to the deck's primary tone; keep inverse-tone
     slides only when they are named story/display exceptions

8. **Viewport-sized card headings**
   - Fix: put `container-type:inline-size` on the card/timeline cell and size
     the heading with `cqw` or a lower max font size

9. **Squeezing card rows into a narrow column while the slide has empty width**
   - Fix: move the card group into a full-width evidence band, widen the layout
     track, reduce the card count, or split the slide

10. **Oversized frame or wide tray around sparse content**
   - Fix: apply `layout-guide.md`'s framed content occupancy and global
     stage-fit rules; shrink or remove the frame, use a compact stage, or
     expand the diagram with meaningful internal structure

11. **Cover uses an explanatory mini-diagram**
   - Fix: remove labeled nodes/cards/arrows from slide 1; keep title, terse
     subtitle/chips, and simple decoration, then move the working diagram to
     slide 2 or a later content slide

12. **Magic Move label wraps during flight then snaps back**
   - Fix: for short labels/chips/badges, use `data-magic-nowrap="true"` or an
     approved label class, and give the source/target the same one-line width
     policy; for real headings, keep the same line-break behavior on both
     sides or animate a shorter stable token instead

13. **SVG route renders as a black blob**
   - Fix: add `fill="none"` and fallback stroke attributes to the source SVG path
   - Avoid: complex masks/filters/blend modes or decorative filled path blobs

14. **Top brand pill becomes a full-width bug bar**
   - Fix: remove direct-child slide chrome, put any necessary mark inside
     `.slide-content`, and avoid long thin top rails entirely
   - Avoid: `.brand-mark` / `.section-no` direct children or browser-bar-like
     strips near the viewport edge

15. **Magic Move labels added only for motion**
   - Fix: move `data-magic-id` to real content such as a heading phrase, card
     title, metric, image/object, or diagram node, or use a hard cut
   - Avoid: repeated `.focus-token`, token rows, chips, or pills appended to
     the body just to create a shared element

## Verification

Before delivery, check:
- [ ] Every slide maps to one approved primary layout primitive
- [ ] All slides use `<section>`, not `<div>`
- [ ] All slides have required attributes
- [ ] Each slide has one real `.slide-content` direct child; any full-bleed
      direct child uses `.bg` and `aria-hidden="true"`; no visible brand marks,
      counters, labels, or other chrome are direct children of `.slide`
- [ ] No generated slide source contains browser/address-bar-like top chrome,
      long thin top rails, or full-width brand pills that could be mistaken for
      runtime UI or a rendering bug
- [ ] Root `.slide` backgrounds and any full-bleed decorative/image layers
      visibly cover the full viewport in slide view and overview thumbnails,
      including wide-screen windows; no `.slide-content`-bounded background
      strip is visible
- [ ] Deck tone mode is consistent: ordinary slides follow the primary
      light/dark mode, and inverse-tone slides are named exceptions with a
      distinct display role
- [ ] Slide 1 is visually distinct from slide 2 and does not reuse ordinary content-slide skeletons
- [ ] Slide 1 H1 is a concise cover title, not a sentence-like topic
      description, and the subtitle is not a mini abstract
- [ ] Slide 1 defaults to a no-image CSS material field unless the user explicitly requested cover imagery
- [ ] Slide 1 does not contain a labeled process diagram, mini architecture
      flow, row of explanatory cards, or card-like nodes with unreadable
      internal text
- [ ] Cover subject image, if present, is not an uploadable wrapper, inset panel, accidental skinny crop, or low-information object strip
- [ ] Palette does not read as gray fog; dark slides, accent blocks, and text all have clear contrast
- [ ] No white/cream/pale-gray or low-opacity text appears on a light/paper field
- [ ] Content text uses opacity/alpha high enough to stay readable; hierarchy is mostly color/token based, not transparency based
- [ ] Magic Move anchors satisfy `flip-engine.md`, including semantic adjacent
      continuity, identical visible text, stable wrap/no-wrap behavior, and no
      decorative-only placeholders, Magic-only token rows, or body labels whose
      main purpose is motion
- [ ] style.css has :root variables and animations
- [ ] Files named slide-01.html, slide-02.html, etc.
- [ ] Layout, text-fit, vertical-balance, source-note, and overlap checks satisfy `layout-guide.md`
- [ ] `.slide-content` is a stable 16:9 design-canvas wrapper; visual tightness
      comes from internal stages/groups rather than global viewport reflow
- [ ] Card groups use available slide width and do not compress paragraph cards
      into unreadably narrow columns while nearby horizontal space is empty
- [ ] Framed main visuals satisfy `layout-guide.md` occupancy rules; no large
      bordered panel is mostly empty around sparse content
- [ ] Sparse mini-flows, chip rows, and small node diagrams satisfy
      `layout-guide.md` stage-fit rules; no full-width pale tray contains a
      tiny centered payload with empty gutters on both sides
- [ ] Ordinary scorecard, comparison, KPI, evidence, and split slides are
      vertically centered unless their main content genuinely fills the height
      budget
- [ ] Metric/card labels do not collide with neighboring cards; four-card
      groups are not squeezed into half-width columns
- [ ] The QA overview longshot was captured only after iframe-loaded readiness,
      then checked by slide number for cramped card rows, escaped labels,
      unreadable wrapping/contrast, overlap, clipping, cropped media,
      wide-tray/tiny-payload layouts, and blank or unloaded cards; unresolved
      `sources/qa/visual-issues.json` notes are repaired from JSON/source
      context before screenshots are used for verification or ambiguous-note
      context
- [ ] Inline SVG connector paths include `fill="none"` and fallback stroke attributes

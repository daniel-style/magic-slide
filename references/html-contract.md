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
- `data-bg` — Background: "dark", "white", "gradient-abstract"

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

## Layout Contract

These rules are non-negotiable because unconstrained HTML/CSS generation is the fastest way to get broken layouts.

1. **Every slide must map to one approved primary layout primitive** from `layout-guide.md`
2. **Do not hybridize root layouts** on one slide just because the content feels ambitious
3. Keep structural depth shallow: `.slide-content` -> one primary layout container -> content blocks
4. If a slide cannot stay clean within one primitive, split it into two slides
5. Prefer stable, proven layout patterns over one-off structural inventions

## Background Contract

Every slide's main background must be owned by the root `.slide` element and
must cover the entire 16:9 viewport. Do not make the apparent background an
inset `.slide-content`, `.stage`, card, panel, pseudo-frame, or centered
rectangle.

Rules:
- Set `background`, `background-size`, `background-position`, and theme variants
  on `.slide` or `.slide[data-bg="..."]`.
- Decorative full-bleed texture may use `.slide::before` / `.slide::after` with
  `position:absolute; inset:0; pointer-events:none`.
- `.slide-content` is a layout wrapper only. It may constrain content width, but
  it must not create the visible page boundary.
- If a theme uses a paper, blueprint, canvas, photo, gradient, or color wash, it
  must visibly reach all four slide edges in both single-slide view and overview
  thumbnails.
- Do not use body background or overview-item fallback color as a substitute for
  a real slide background.

## Cover Contract

Slide 1 must be a true cover, not an ordinary content slide wearing a title.

Rules:
- `slide-01.html` must use a dedicated cover/display composition.
- The cover must be visually distinct from slide 2 in layout skeleton, scale,
  density, and focal element.
- Default cover background is no-image. Use a premium minimalist CSS material
  field on the root `.slide`: restrained gradients, subtle pattern or texture,
  strong typography, and whitespace. It must read as grand, simple, and
  high-end in the first second.
- Do not use a generated/photo cover background unless the user explicitly
  asked for cover imagery or the topic requires a recognizable product/place/
  object on slide 1.
- Avoid repeated cards, ordinary memo grids, dense tables, or the same
  two-column layout used in subsequent slides.
- The cover may share one semantic Magic Move element with slide 2, such as the
  title, logo, or key phrase, but the rest of the composition should clearly
  change role after the opening.
- The cover should have one primary focal object: hero title, product/object
  image, iconic diagram, typographic crop, or strong material field.
- If the cover uses a subject image, it must be full-bleed, a wide hero panel,
  a mostly visible product/object, or an abstract material field. Do not crop a
  landscape image into a tall skinny strip or arbitrary object sliver.
- Never implement the apparent cover background as an uploadable image wrapper,
  inset panel, or document-flow image. Cover imagery, when explicitly allowed,
  must be owned by the root `.slide` background or a full-bleed absolutely
  positioned decorative layer behind `.slide-content`.

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
- If the full text cannot fit, reduce the max font size, widen the container, allow wrapping, or split the slide.
- Do not hide text overflow with `overflow:hidden`, `overflow:clip`, masks, or
  fades. If content needs hiding to look tidy, the slide is over budget.

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
used intentionally and do not appear on decorative-only elements.

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
placement, and overflow/collision policy.

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

7. **Viewport-sized card headings**
   - Fix: put `container-type:inline-size` on the card/timeline cell and size
     the heading with `cqw` or a lower max font size

8. **Squeezing card rows into a narrow column while the slide has empty width**
   - Fix: move the card group into a full-width evidence band, widen the layout
     track, reduce the card count, or split the slide

9. **SVG route renders as a black blob**
   - Fix: add `fill="none"` and fallback stroke attributes to the source SVG path
   - Avoid: complex masks/filters/blend modes or decorative filled path blobs

## Verification

Before delivery, check:
- [ ] Every slide maps to one approved primary layout primitive
- [ ] All slides use `<section>`, not `<div>`
- [ ] All slides have required attributes
- [ ] Root `.slide` backgrounds visibly cover the full viewport in slide view and overview thumbnails
- [ ] Slide 1 is visually distinct from slide 2 and does not reuse ordinary content-slide skeletons
- [ ] Slide 1 defaults to a no-image CSS material field unless the user explicitly requested cover imagery
- [ ] Cover subject image, if present, is not an uploadable wrapper, inset panel, accidental skinny crop, or low-information object strip
- [ ] Palette does not read as gray fog; dark slides, accent blocks, and text all have clear contrast
- [ ] No white/cream/pale-gray or low-opacity text appears on a light/paper field
- [ ] Content text uses opacity/alpha high enough to stay readable; hierarchy is mostly color/token based, not transparency based
- [ ] Magic Move anchors satisfy `flip-engine.md`
- [ ] style.css has :root variables and animations
- [ ] Files named slide-01.html, slide-02.html, etc.
- [ ] Layout, text-fit, vertical-balance, source-note, and overlap checks satisfy `layout-guide.md`
- [ ] Card groups use available slide width and do not compress paragraph cards
      into unreadably narrow columns while nearby horizontal space is empty
- [ ] Inline SVG connector paths include `fill="none"` and fallback stroke attributes

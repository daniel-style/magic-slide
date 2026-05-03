# FLIP Engine — Magic Move Implementation

The exact JavaScript code for the FLIP (First-Last-Invert-Play) animation engine. This is **injected automatically** by `<magic-slide-path>/scripts/inject-runtime.py` — you never write it manually.

## Design principle: only one animated shared instance may exist at a time

The core Magic Move effect: shared elements (those with `data-magic-id` appearing on both consecutive slides) should read as one continuous object moving from slide N to slide N+1.

**Current runtime rule:** during the FLIP motion, there must be **exactly one animated visual instance** of each shared element on screen. This avoids the "ghost" artifact caused by overlapping FROM/TO versions of the same element.

## How the engine works

1. **Capture FROM positions** — record bounding rects of all shared elements on the current slide
2. **Measure TO positions** — briefly activate the target slide off-screen/invisible to capture final rects
3. **Create one TO clone** — clone the TO element, snapshot its computed styles, and give it a fixed-position TO-sized layout box
4. **Apply inverse FLIP** — move that single TO clone back to the FROM geometry using a 2D transform matrix, so translate, scale, and rotation/skew all participate in the motion
5. **Hide originals** — hide the FROM original immediately and hide the TO original until cleanup
6. **Animate** — the single TO clone flies to its natural TO position while the target slide runs its page transition and non-shared content staggers in
7. **Cleanup** — reveal the real TO original and remove the clone in the same cleanup phase

## Key implementation details

### Why the runtime no longer uses dual-clone crossfade

An older runtime tried to handle unstable matches with two simultaneously rendered versions:
- one FROM clone fading out
- one TO clone fading in

That looked acceptable in theory, but in real decks it produced obvious ghosting:
- duplicated glyph edges
- dark or gray shadow copies behind the moving element
- overlap that became visible in captured animation frames

The current runtime fixes this by using a **single TO clone** even for less-stable matches. This is a stricter rule than the older "crossfade similar nodes" strategy, but it removes ghosting at the engine level.

### Why visibility:hidden still matters on FROM

In v1, the FROM slide faded opacity from 1→0 via CSS transition. This caused flickering because:
- Shared elements on the TO slide were visually at the FROM position (via inverse transform)
- But the FROM slide's shared elements were *also* still visible and fading
- The two overlapping elements created a visual "double" that looked broken

The fix: set FROM slide to `visibility:hidden` **instantly** (no transition), which removes FROM content from the render tree immediately. The animated TO clone is then the only visible shared element during motion.

### Non-magic element detection

The engine reveals non-magic content on the TO slide with staggered entrance animations. It chooses the real content root by preferring `.slide-content`, so decorative direct children such as rails or background accents do not steal the stagger pass.

Within that content root:
- Elements WITHOUT `data-magic-id` → enter with staggered delay
- Elements WITH `data-magic-id` → FLIP animated
- Layout wrappers are traversed recursively so nested cards, list rows, and timeline items can stagger individually
- Text blocks such as headings and paragraphs stagger as whole blocks, even
  when they contain inline language spans. Do not push stagger classes down to
  ordinary inline spans; transforms on inline text are visually unreliable.
- Text-block stagger needs to be perceptible at presentation scale. The runtime
  gives stagger items a small base delay after the slide swap starts, and gives
  heading/lead text blocks a longer, larger rise than ordinary UI chips or
  cards so the first large text item does not disappear into the page
  transition.
- Containers that hold shared Magic Move elements are protected from duplicate animation where needed

Slide-level `data-stagger="none"` is reserved for explicit no-animation
requests. During injection, accidental `none` values are normalized to
`cascade` unless the slide also declares `data-stagger-disabled="true"`.
This protects generated decks from losing all non-magic entrance motion when
Magic Move shared elements are present.

### z-index management during transition

- TO slide: `z-index: 2` (on top of FROM)
- Shared TO clones: `z-index: 9999` (highest priority during animation)
- All z-indexes cleared on cleanup

### Clone layout preservation

The runtime must not replace a clone's entire inline `style` string. Magic-id text often uses inline layout guards such as `display:inline-block`, `white-space:nowrap`, or `max-inline-size` to keep its measured line breaks stable. During FLIP, the runtime now keeps the cloned element's existing inline styles, snapshots layout-critical computed styles (`display`, `box-sizing`, flex gap/alignment, typography, wrapping), then applies only the fixed-position geometry needed for the animation.

This prevents a label from wrapping during the animated clone phase and snapping back to one line when the real TO element is revealed.

### Generated source contract for text anchors

Every text element with `data-magic-id` must render as a stable box. Author
text anchors with `display:inline-block` or a class that computes to
`inline-block`; do not put `data-magic-id` on a raw inline `span`, `strong`, or
`em` and expect the browser's inline line box to animate smoothly.

For cover-title -> section-title or phrase -> title moves, the source and
target must have compatible box roles:
- Whole-heading anchors: use the whole heading on both slides, and make both
  headings `display:inline-block`.
- Phrase anchors inside headings or paragraphs: make the phrase element
  `display:inline-block` on both slides, with identical visible text and
  compatible `text-transform`, `white-space`, and width policy.
- Short display headings that are intended to stay on one line should use a
  one-line heading style on both sides, such as `display:inline-block;
  white-space:nowrap`, plus a font-size cap or wider container that proves the
  phrase fits. Do not use `data-magic-nowrap="true"` for heading phrases; that
  attribute is reserved for labels/chips/badges.

If a phrase appears as an inline word in a paragraph on slide N and becomes a
large `h1`/`h2` on slide N+1, first decide whether it is a one-line display
phrase or a multiline heading. If the destination would wrap while the source
does not, either widen/lower the destination heading so it remains one line,
split the phrase into semantic inline-block fragments, or remove the
`data-magic-id`. A one-line phrase that breaks during the FLIP animation is a
broken anchor, even when the final slide looks acceptable.

The snapshot also includes size constraints (`min-width`, `min-height`,
`max-width`, `max-height`, and inline-size equivalents). FLIP clones are moved
to `body`, so selectors that depend on the slide ancestry no longer match.
Without these computed constraints, a clone can fall back to a generic card or
plate `min-height` and then visibly shrink or grow when the real target element
is revealed. In the no-wrap label path, these constraints are scaled to the
visual rect just like font size, line height, and padding, so clones inside
runtime-scaled slide wrappers still match the target at cleanup.

Short text marks such as `.small-mono`, tags, badges, `.section-tag`,
`.mini-label`, `.mini`, `.endpoint`, `.feature-plate`, legacy `.deck-mark`, and
simple inline-flex/inline-block labels use the no-wrap label path when they
already exist in a deck. Their animated clone keeps `white-space: nowrap` and
animates fixed geometry, font size, line height, padding, and border widths
instead of relying on a single transform scale. This keeps one-line marks from
wrapping or snapping to a different text metric when the clone is replaced by
the real target element on cleanup. This runtime support is not permission to
invent Magic-only labels or deck chrome.

Use `data-magic-nowrap="true"` only on short custom label/chip elements that
must remain one line and behave like labels. It is not for heading phrases,
card titles, hero-card titles, callout titles, or ordinary `.magic-phrase`
spans, even when the text is only two or three words. The source and target
still need enough width for the string: if the label cannot fit on one line,
widen the container, lower the font-size max, or remove the nowrap promise.

Shared text anchors need stable line behavior. A label that wraps during the
animated clone and then becomes one line at the destination is a broken Magic
Move. Before writing HTML, decide whether each shared text anchor is a
one-line label or a multiline heading/body block:
- One-line labels: use an approved label class or `data-magic-nowrap="true"`
  and keep both source and target to the same nowrap policy.
- One-line display headings/phrases: use `display:inline-block` plus an
  authored one-line width policy on both sides; do not use
  `data-magic-nowrap="true"` unless the element is actually a label/chip.
- Multiline headings/body text: let both sides wrap naturally with compatible
  widths, and do not add `data-magic-nowrap="true"` to the phrase. If the
  whole text block is too unstable, anchor a shorter phrase or split it into
  semantic fragments.
- If only a short phrase is stable, put `data-magic-id` on that phrase rather
  than on the card, panel, or paragraph wrapper.

When a slide wrapper has been scaled by runtime fit logic, the runtime lays out each clone using the TO element's unscaled `offsetWidth` / `offsetHeight`, then animates to the visual `getBoundingClientRect()` scale. This keeps text layout based on the same width budget as the real element instead of forcing unscaled typography into a smaller transformed rect.

For ordinary Magic text, including `.magic-phrase`, the runtime treats the
element as text rather than as a label. The animated clone gets a fixed TO-sized
layout box and moves with `transform`; if the TO element renders as one line,
the clone is also locked to one line for the whole transition. This prevents the
mid-animation state from wrapping at an interpolated width and then snapping
back when the real TO element is revealed.

For normal Magic Move clones, the runtime represents the FROM and TO visual
states as viewport-space 2D matrices rather than only axis-aligned rectangles.
This preserves rotated or skewed endpoints: an element whose target state uses
`transform: rotate(...)` rotates during the FLIP animation instead of snapping
to the angle only after cleanup. Short no-wrap labels continue to use their
font/geometry interpolation path only when neither side has a transform; labels
with transforms use the matrix path.

## Helper function

```js
function getMagic(slide) {
  var els = {};
  slide.querySelectorAll('[data-magic-id]').forEach(function(el) {
    els[el.dataset.magicId] = el;
  });
  return els;
}
```

## Good and bad magic-ids

### Good magic-ids

| Source | Target | Why it works |
|---|---|---|
| Cover `<h1>` "LangChain" (center, giant) | Section `<h2>` "LangChain" (left, smaller) | Same text, heading→heading, travels + shrinks |
| Card `<h3>` "Models" in grid | Giant `<h2>` "Models" on detail slide | Same text, heading→heading, 4× size increase |
| Small stat "600+" in list | Giant "600+" on its own slide | Same text, same concept, dramatic size change |
| Card `<div>` (title+desc) | Same card `<div>` larger | Same structure, card→card, expansion |

### Bad magic-ids

| Source | Target | Why it fails |
|---|---|---|
| "Ecosystem" h2 | "Get Started" h2 | Different text — audience sees one word morph into another |
| Card `<div>` with title+text | Bare `<h2>` heading | Container mismatch — card content stretches/distorts during FLIP |
| Ghost watermark (opacity:0.04) | Any content element | Invisible decorative element flashes during animation |
| "Next: Models" preview `<div>` | `<h2>` "Models" heading | Different text + invented element + container mismatch |
| `<span>` inside heading | Heading on another slide | Span has tiny bounding rect — invisible animation |

### Hard limits

- **No hard numeric cap.** Use as many shared `data-magic-id` elements as are genuinely the same thing and improve readability of the move.
- **Only consecutive slides.** An element on slide 2 and slide 5 won't animate. It must appear on every slide in between.
- **No ghost watermarks** as magic-id targets. They're decoration only.

## Planning for richer Magic Move decks

Treat Magic Move as part of the narrative structure, not just a title trick. Before writing adjacent slides, quickly map which elements should persist.

Plan this before HTML, ideally while writing or refining the outline. A strong
Magic Slide deck usually contains a visible continuity spine: concepts pass
between slides as premise, focus, detail, contrast, or resolution. That often
looks like overview items expanding into detail slides, small numbers becoming
hero stats, system nodes becoming zoomed diagrams, or evidence cards becoming
case-study layouts. If the planned deck has no natural shared elements,
improve the content sequence before trying to patch motion into finished
slides.

### Primary Magic Move anchors

For each adjacent pair with continuous subject matter, plan one **primary**
Magic Move anchor. Supporting anchors can add context, but the primary anchor
is the element that makes the audience feel the idea carried forward.

A primary anchor must be:

- **Semantic** — it is truly the same concept, object, metric, date, card,
  image, or diagram node on both slides.
- **Content-bearing** — it is part of the slide's main argument, not a footer,
  watermark, corner label, purely decorative mark, or tiny navigation chip.
- **Visually meaningful** — at least one side treats it as a main card, heading
  phrase, hero number, image/object, comparison row, timeline date, or diagram
  node.
- **Role-changing** — it changes scale, position, crop, grouping, or narrative
  role; a static label that barely moves is only a supporting anchor.
- **Implementation-safe** — any text used for the shared `data-magic-id` has
  identical visible text and compatible text transform on both slides.

Content stays first: never alter facts, wording accuracy, or logical order just
to make a Magic Move possible. The fix for weak motion is to arrange the
argument into real relay beats: overview -> detail, setup -> reveal,
map -> zoom, compare -> case, metric -> implication, or question -> answer.

Long display titles are usually poor Magic Move anchors when the target is a
small deck mark or navigation label. Let the hero title wrap and behave like
normal slide typography; put `data-magic-id` on a shorter stable phrase inside
real content, or skip the move. A one-line forced `h1` or artificial chip is
not worth the overflow or ambiguity risk.

Card, hero-card, callout, and metric headings follow the same rule. Never mark
a card title phrase as `data-magic-nowrap="true"` just because it needs to move
to the next slide. Size it from the card/container, allow wrapping, or use the
phrase-fragment pattern below.

When a real long phrase must carry the transition, split it into semantic
phrase fragments instead of animating one long text box. Each fragment gets its
own `data-magic-id`, identical visible text, and `display:inline-block`; a
parent heading controls alignment, line breaks, and gap. This keeps the visual
layout honest on each slide while letting the words travel independently.

Use this pattern for phrase-level anchors:

```html
<h1 class="relay-title">
  <span data-magic-id="closing-change-models" style="display:inline-block">change models,</span>
  <span data-magic-id="closing-not-products" style="display:inline-block">not products</span>
</h1>
```

The fragments should be natural reading units, not arbitrary word confetti:
short clauses, noun phrases, number + unit pairs, or the emphasized contrast in
a sentence. Keep punctuation with the fragment where readers hear it. If the
source slide needs two lines and the target slide needs one line, author that
line layout on the parent container with normal CSS; do not force a single
nowrap magic element just to satisfy FLIP.

### No Magic-only labels

Do not create visible labels whose main job is to become Magic Move targets.
Labels, chips, badges, pills, and token rows are legitimate only when they are
already necessary content: a real status, category, timeline date, card title,
diagram node label, or row label. If a label would be ambiguous in the body
without the animation, remove it or keep it non-magic.

Avoid these patterns:
- Repeated `.focus-token` / token rows appended near the bottom of body slides.
- "Next topic" chips that preview the following slide.
- Small brand marks, footers, page numbers, or chapter pills used as primary
  anchors.
- A deck-wide "magic label" system that exists mainly to satisfy transition
  density.

Use Magic Move on the content the audience is already reading: a heading phrase,
card title, metric, image/object, comparison row, timeline date, or diagram
node. If there is no natural shared content, use a hard cut with a story reason
or revise the slide sequence.

**Good recurring anchors:**
- Agenda/list items that expand into full section headings
- Card titles or key phrases that move from overview to detail
- Numbers, dates, and short labels that become hero stats
- Reused product shots, diagrams, or illustrations that change crop or scale

**Practical density guidance:**
- Most adjacent slides with overlapping subject matter should share at least 1 meaningful element
- For decks with 5+ slides, aim for primary Magic Move anchors on a majority of adjacent pairs unless the outline has explicit hard cuts
- Overview/detail or zoom-in sequences often support 1 primary anchor plus 1-3 supporting anchors
- The cover should usually hand off one stable title, image, or key phrase into slide 2, then the ordinary deck should continue with its own recurring content anchors
- A tiny global deck mark, footer, page number, or section chip should normally
  stay non-magic. If it persists, it does not count as a primary anchor or as
  the deck's Magic Move selling point by itself. Add local/content anchors that
  change scale, position, or role between adjacent slides.
- If an audit shows only one or two shared pairs in a normal-length deck, revise the outline or slide treatment before final polish
- If only one small part of a block is truly stable, animate that sub-element instead of the whole wrapper
- Tag changes are fine when the semantic entity is clearly the same and the visible text still matches
- Do not add placeholder duplicates, body token rows, or Magic-only labels
  purely to manufacture motion

---

## Example magic-id chain — good pattern

```
Chain table with movement annotations (verify before writing HTML):
  Slide 1 agenda:   [title-main=h1 center "ML 101"] [topic-data=small list item "Data Preparation"] [topic-model=small list item "Model Training"]
  Slide 2 data:     [title-main=h1 left "ML 101"] [topic-data=giant h2 "Data Preparation"]
                     ↑ title-main: centered h1 → left-aligned h1 = travels left, shrinks 2× ✓
                     ↑ topic-data: list item → giant heading = same text "Data Preparation", 4× size ✓
  Slide 3 model:    [title-main=h1 left "ML 101"] [topic-model=giant h2 "Model Training"]
                     ↑ title-main: same position, same size = supporting element ✓
                     ↑ topic-model: list item → giant heading = same text "Model Training", 4× size ✓
  Every adjacent pair shares only semantically stable ids, every shared element has the SAME TEXT on both slides ✓
```

```html
<!-- Slide 1: Agenda -->
<section class="slide slide-center" data-id="agenda">
  <div style="position:relative;z-index:1;text-align:center">
    <h1 data-magic-id="title-main" style="display:inline-block;font-size:clamp(3rem,7vw,5rem)">ML 101</h1>
    <ul style="margin-top:2rem;text-align:left;display:inline-block">
      <li data-magic-id="topic-data" style="font-size:1.1rem">Data Preparation</li>
      <li data-magic-id="topic-model" style="font-size:1.1rem">Model Training</li>
    </ul>
  </div>
</section>

<!-- Slide 2: Data — title-main moves from center to left; topic-data becomes giant heading -->
<section class="slide" data-id="section-data">
  <div style="position:relative;z-index:1;padding:4rem;max-width:1100px">
    <h1 data-magic-id="title-main" style="display:inline-block;font-size:clamp(1.5rem,3vw,2rem);font-weight:600">ML 101</h1>
    <h2 data-magic-id="topic-data" style="display:inline-block;font-size:clamp(2.5rem,6vw,4.5rem);margin-top:2rem">Data Preparation</h2>
    <p style="margin-top:1rem;max-width:520px;color:var(--subtext)">Clean inputs, feature engineering, train/val/test split.</p>
  </div>
</section>

<!-- Slide 3: Model — title-main stays put; topic-model becomes giant heading -->
<section class="slide" data-id="section-model">
  <div style="position:relative;z-index:1;padding:4rem;max-width:1100px">
    <h1 data-magic-id="title-main" style="display:inline-block;font-size:clamp(1.5rem,3vw,2rem);font-weight:600">ML 101</h1>
    <h2 data-magic-id="topic-model" style="display:inline-block;font-size:clamp(2.5rem,6vw,4.5rem);margin-top:2rem">Model Training</h2>
    <p style="margin-top:1rem;max-width:520px;color:var(--subtext)">Architecture, loss functions, optimisers, evaluation.</p>
  </div>
</section>
```

---

## Critical CSS consistency rule for magic-id pairs

**RULE: Elements connected by the same `data-magic-id` MUST have identical `text-transform` values.**

The runtime classifies matches internally, but the core problem remains the same: `text-transform` changes how text *renders* without changing `textContent`. If FROM has `text-transform:uppercase` and TO has `text-transform:none`, the browser shows different text ("ROADSTER" vs "Roadster") even though `textContent` is identical ("Roadster").

**What happens if mismatched:**
- During animation, the clone element's `text-transform` interpolates from FROM to TO
- Text visually "jumps" mid-flight when the transform switches (uppercase → lowercase or vice versa)
- Looks broken and jarring

**How the runtime protects against this:**
The runtime checks `getComputedStyle().textTransform` and other text-layout signals to classify unstable matches. Those unstable matches still animate with a single inverse-FLIP TO clone, but mismatched text transforms remain a red flag because the animation will still feel less clean than a genuinely stable pair.

**How to avoid it in HTML generation:**
1. If FROM element has a class with `text-transform` (e.g. `.tag { text-transform: uppercase }`), TO element must have the same transform
2. Use inline `style="text-transform:uppercase"` on TO if it doesn't have the same class
3. Or remove the magic-id entirely if the text casing difference is intentional

**Example — WRONG:**
```html
<!-- Slide A: tag with uppercase -->
<span class="tag" data-magic-id="product-name">Roadster</span>
<!-- .tag has text-transform:uppercase → renders "ROADSTER" -->

<!-- Slide B: heading without transform -->
<h2 data-magic-id="product-name">Roadster</h2>
<!-- No transform → renders "Roadster" -->
<!-- ✗ Text jumps from "ROADSTER" to "Roadster" mid-animation -->
```

**Example — CORRECT:**
```html
<!-- Slide A: tag with uppercase -->
<span class="tag" data-magic-id="product-name">Roadster</span>

<!-- Slide B: heading with matching transform -->
<h2 data-magic-id="product-name" style="text-transform:uppercase">Roadster</h2>
<!-- ✓ Both render "ROADSTER", smooth animation -->
```

---

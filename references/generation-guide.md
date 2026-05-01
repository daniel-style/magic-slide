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

`step-04-design-brief.md` is the authority for the brief's exact fields and
hard-stop checks. `design-system.md` is the authority for visual differentiation
and anti-template warnings. Do not duplicate those detailed rules here.

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
   more memorable than ordinary content slides, with concise title-like cover
   copy.
4. **Visible hierarchy.** Each slide needs a clear focal element and supporting
   context.
5. **Purposeful variety.** Repetition is allowed only when it creates a
   deliberate sequence.
6. **Magic Move continuity.** Plan semantic elements across adjacent slides
   before writing HTML, then reuse them when the story naturally continues.
7. **Text fits by design.** Do not rely on runtime rescue, hidden overflow, or
   manual browser edits.

## Cover Distinction

Before writing `slide-01.html`, define its display role separately from the
deck's normal slide families. The cover should be a title sequence frame,
poster, product reveal, book cover, exhibition wall, hero image, or strong
material/typographic field. For product, AI, infrastructure, SaaS, and
developer-tool decks, default to title plus minimal labels and simple
decoration; do not put the working architecture, request pipeline, feature
cards, or explanatory node diagram on slide 1. Move that model to slide 2 or a
later content slide.

Use `design-system.md` for the cover's visual role and `images.md` for cover
image policy. Use `html-contract.md` for the verifiable cover checklist. The
generation task here is only to decide the cover role before ordinary slide
families are written, including the short display title and where any longer
scope wording moves.

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
If a horizontal split wants three or more cards in one column, it is no longer
a split slide. Promote the card group to a full-width evidence band, use a
dedicated Metrics/Grid primitive, or split the idea. Do not shrink word-based
metric cards until their titles collide.

Plan card-grid parity before writing CSS. A known even card count must not
render with an orphan final row: four cards should be `2x2`, six cards should be
`3x2` or `2x3`, and eight cards should be `4x2` or `2x4`. Use explicit
`repeat(2, minmax(0, 1fr))`, `repeat(3, ...)`, or `repeat(4, ...)` grids for
known counts instead of `auto-fit`/`auto-fill` when those automatic grids can
produce `3+1`, `5+1`, or another single-card row. If the available width cannot
support the symmetric grid, move the group to a full-width band, split it, or
stack it cleanly at the breakpoint.

Keep ordinary slides vertically centered. Add top alignment only for genuinely
dense tables, matrices, long timelines, or complex diagrams that fill most of
the usable slide height. A compact scorecard or card grid with a large empty
area below is a broken vertical-balance slide, not a dense slide.

`layout-guide.md` is the authority for primitives, text fit, overflow,
collision budgets, vertical balance, and source-note placement. `html-contract.md`
is the authority for root slide backgrounds, required structure, SVG, and
verification. Keep this guide focused on the planning pass, then consult those
references while authoring.

Choose the deck's primary tone mode before scaling the deck. Brief Lite and the
internal production plan must name the primary light/dark mode and any
inverse-tone exceptions. Use `html-contract.md` as the authority for root
backgrounds, `data-bg`, and when inverse-tone slides are allowed.

Avoid repeated visible skeletons. In a 30-slide deck:

- No single layout signature should dominate.
- `title + three cards` should be rare and justified.
- `image left + text right` should vary by crop, hierarchy, or purpose.
- Chips and badges should act as navigation, status, grouping, or data labels,
  not decoration.
- If three consecutive slides share the same title block, accent line, grid, and
  card treatment, rewrite one before continuing.

## Text Fit

Clipped text is a broken slide. Use `layout-guide.md` for sizing, wrapping,
container-width budgets, and overflow policy.

## Required Slide Structure

Follow `html-contract.md` for the exact slide-fragment structure, required
attributes, stagger policy, file naming, and prohibited elements.

## Style System

`style.css` should implement Brief Lite, not a generic template.

Include:

- `:root` variables for motion, core colors, typography, and reusable spacing.
- Base slide and `.slide-content` layout.
- Typography hierarchy.
- The deck-specific components actually needed by the story.
- Motion keyframes used by slide transitions and non-Magic Move entrances.
- Responsive text and container rules.
- Official brand/logo handling when the topic has a real brand: use verified
  assets from the supplied URL or a text-only label; never invent pseudo-logos
  or decorative marks beside a brand name.

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

Read `references/images.md` before generating or placing images. It is the
authority for generated image prompts, uploadable wrappers, background-image
policy, and cover-image handling.

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
- Follow `images.md` for content-image wrappers and background-image policy.

## Magic Move Strategy

Before coding all slides, map adjacent slide pairs. This is an editorial pass,
not a post-generation audit. If the map is thin, revise the outline, slide
order, or slide treatment before generating HTML.

Use `flip-engine.md` as the authority for `data-magic-id` rules and runtime
behavior. Before full generation, write a compact continuity map that covers
each adjacent pair, then carry that map into the HTML as you write each
affected slide pair.

The continuity map should include:

- The adjacent pair, such as `slide-03 -> slide-04`.
- The content relationship: continuation, amplification, decomposition,
  contrast, return, or chapter break.
- Primary vs supporting anchors. Use `flip-engine.md` as the authority for the
  primary-anchor quality standard.
- Planned id names, exact visible text, and element type on both sides.
- The motion role: travel, shrink, expand, zoom into detail, remain as deck
  mark, or carry chapter context.
- Any intentional hard cut, with a story reason.

Default density target:

- In decks with five or more slides, most adjacent pairs should share a primary
  Magic Move anchor unless they are intentional hard cuts.
- Overview/detail, agenda/section, system-map/zoom, timeline/detail, and
  metric/setup sequences should usually share one primary anchor plus 1-3
  supporting anchors.
- A deck where only the cover title moves once is underusing the skill. Fix
  the outline or slide treatment before polishing CSS.
- Never add decorative duplicates, hidden ghosts, or fake repeated labels just
  to satisfy density. The fix is content arrangement: stable labels, chapter
  markers, card titles, key numbers, images, and diagram nodes that are truly
  the same thing.
- Hard stop before HTML: if the continuity map mostly says "none" or repeats
  only a footer, corner label, tiny global deck mark, watermark, or pure
  chapter chip, do not proceed. Re-sequence the content into index-to-detail,
  setup-to-reveal, map-to-zoom, or compare-to-case beats until the Magic Move
  opportunities are real.

## Objective QA

After generating the full deck:

- Read beginning, middle, and end slide fragments.
- Check all slides use the required structure and file names.
- Check the deck tone mode: ordinary slides follow the primary light/dark mode,
  and every inverse-tone slide is a named exception with a distinct display
  role.
- Check Magic Move continuity against `flip-engine.md`.
- Check branded marks against `html-contract.md`: official logo or text-only,
  no fabricated symbols, no arbitrary pseudo-elements that read as logo
  fragments.
- Check the cover against `layout-guide.md`: decorative linework, nodes, traces,
  grids, and pseudo-elements must not cross or compete with the title,
  subtitle, wordmark, or chip row.
- Check the cover against `html-contract.md`: the H1 must be concise, and the
  subtitle must not become a mini abstract; for product/AI/infrastructure decks,
  the cover must not contain a readable process diagram or explanatory card
  flow.
- Check inline SVG against the visual quality contract, not only the black-blob
  safety rules: diagrams need hierarchy, aligned labels, line rhythm, and
  enough structure to read as finished graphics.
- During source review, compare the generated `data-magic-id` anchors against
  the pre-code continuity map. Fix local omissions in the affected source
  slides; do not use final QA as the first moment to invent the Magic Move
  structure.
- Merge slides with `merge-slides.py`.
- Inject runtime with `inject-runtime.py`.
- Preview with `serve.py`.
- Run the QA overview gate from `step-10-preview.md` before detailed viewport
  checks. Open `?ms_qa=overview`, scan every card, and if user review is needed,
  stop for them to request revisions saved in `sources/qa/visual-issues.json`.
- Read unresolved revision notes first. Treat those slides as known repair
  targets, then review QA overview screenshots for additional visual problems on
  unmarked slides. The overview is intentionally not a rule-based detector; it
  exists to make the remaining rendered deck easy to inspect.
- When repairing, use both the JSON notes and any new screenshot findings, fix
  `sources/`, then merge, inject, preview, and capture QA overview again.
- After verification, mark repaired JSON records `resolved: true`; do not write
  revision notes into `index.html`.
- Run browser or manual viewport checks on every slide at a normal 16:9 viewport
  and a smaller 16:9 viewport, such as `1440x900` and `1024x576`.
- Check for overflow, clipped text, broken images, dead zones, unbalanced
  columns, sparse framed panels, and runtime fit issues using
  `step-10-preview.md` as the delivery checklist.
- In full-size visual review, revise any slide that looks cramped, clipped,
  scaled down, or unbalanced.
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

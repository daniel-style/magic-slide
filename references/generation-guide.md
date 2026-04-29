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

Use `design-system.md` for the cover's visual role and `images.md` for cover
image policy. Use `html-contract.md` for the verifiable cover checklist. The
generation task here is only to decide the cover role before ordinary slide
families are written.

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

`layout-guide.md` is the authority for primitives, text fit, overflow,
collision budgets, vertical balance, and source-note placement. `html-contract.md`
is the authority for root slide backgrounds, required structure, SVG, and
verification. Keep this guide focused on the planning pass, then consult those
references while authoring.

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

Before coding all slides, map adjacent slide pairs.

Use `flip-engine.md` as the authority for `data-magic-id` rules and runtime
behavior. Before full generation, write a compact continuity map that covers
each adjacent pair, then verify the actual IDs after generation.

## Objective QA

After generating the full deck:

- Read beginning, middle, and end slide fragments.
- Check all slides use the required structure and file names.
- Check Magic Move continuity against `flip-engine.md`.
- Merge slides with `merge-slides.py`.
- Inject runtime with `inject-runtime.py`.
- Preview with `serve.py`.
- Run browser or manual viewport checks on every slide at a normal 16:9 viewport
  and a smaller 16:9 viewport, such as `1440x900` and `1024x576`.
- Check for overflow, clipped text, broken images, dead zones, unbalanced
  columns, and runtime fit issues using `step-10-preview.md` as the delivery
  checklist.
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

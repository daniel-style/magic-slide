# Design System - Aesthetic Direction

Create distinctive, production-grade presentations with a clear point of view.
This document is a design decision framework, not a CSS recipe. Do not treat it
as a list of visual ingredients to satisfy.

## Core Principle

Before writing CSS or slide HTML, define the deck's art direction in Brief Lite.
Keep it short by default, but make it specific enough that another topic could
not be swapped in without changing the design.

Answer these questions:

1. **Purpose:** What is the deck trying to make the audience understand, feel,
   or decide?
2. **Audience and setting:** Who watches it, and in what context: conference,
   boardroom, classroom, investor memo, product walkthrough, internal review?
3. **Tone:** Pick a clear direction: brutally minimal, editorial, industrial,
   playful, luxurious, academic, operational, documentary, raw, cinematic,
   archival, field-notebook, product-teardown, museum-label, and so on.
4. **Visual world:** Name the world you are borrowing from: annual report,
   factory operations manual, architecture monograph, research poster, trading
   terminal, hardware teardown, fashion lookbook, film title sequence, lab
   notebook, exhibition wall text, etc.
5. **Differentiation:** What is the one thing someone will remember visually?
6. **Forbidden tropes:** Name two obvious topic tropes you will avoid.
7. **Motif:** Choose one structural motif that can recur across slides without
   becoming decoration for its own sake.

The right level of ambition depends on the direction. Maximalist decks need
rich composition and motion. Minimal or refined decks need restraint, exact
spacing, careful typography, and disciplined detail.

## Auto Style Means Choose, Not Default

When the user chooses an automatic style, do not use the first visual language
that comes to mind. First name three plausible visual worlds, then reject at
least two with a short reason. Choose the one that best fits the story, audience,
and available content.

For company, technology, AI, finance, or product decks, the first idea is often
also the most generic. A dark grid, brand accent color, UI font, chips, and
three metric cards may be appropriate only if the concept adds a more specific
point of view. Otherwise it is a template, not an art direction.

## Deck Spine And Visual Grammar

A strong deck is not 30 independently styled pages. Before building the full
deck, define the spine that makes the pages feel directed:

- **Thesis spine:** the 1-2 sentence argument the whole deck keeps proving.
- **Chapter spine:** the major turns in the story, including how the closing
  resolves the opening.
- **Slide families:** 4-6 reusable families such as hero thesis, evidence/data,
  image evidence, system diagram, risk map, timeline, comparison, or closing.
  Each family needs a role in the story, not just a layout shape.
- **Recurring anchors:** labels, section markers, chips, key numbers, images, or
  title fragments that can persist with Magic Move across adjacent slides.
- **Detail budget:** what makes a normal slide feel finished: source note,
  caption, diagram label, proportional bar, crop decision, callout, rail,
  sequence number, texture, or another subject-specific detail.
- **Image and data treatment:** how images, figures, captions, and sources will
  be integrated into the composition instead of pasted into generic rectangles.
- **Content budget:** the maximum visible burden each slide family can carry:
  focal element, 1-2 supporting blocks, and a reserved caption/source/detail
  area when needed.

If the slide families are only "title + cards", "title + bullets", and "image
plus bullets", the deck does not yet have a visual grammar. Revise the concept
before writing the full deck.

## What Good Looks Like

A strong deck feels designed for its subject. It has:

- A coherent visual world, not a generic "modern tech" wrapper.
- Typography chosen for character, mood, and legibility, not from a memorized
  list.
- A color system with hierarchy and restraint, where accent colors have jobs.
- Slide compositions that vary because the story changes, not because random
  decorations were added.
- Backgrounds and details that support the concept: image crops, rule lines,
  texture, diagrams, whitespace, density, physical materials, or atmosphere.
- Motion that clarifies continuity and emphasis, especially through Magic Move.

## Anti-Template Warnings

These are qualitative smells, not scriptable rules. If the deck starts to look
like one of these, stop and choose a more specific art direction:

- **Tech noir autopilot:** black background, neon green or cyan, condensed
  display font, glow borders, metric cards, grid/noise background.
- **Scary green infrastructure:** acid-green or saturated brand-green wash,
  circuit-board traces, terminal motifs, ominous dark gradients, and all-caps
  condensed type pretending to be strategy.
- **SaaS metrics template:** huge number, tiny label, three cards, repeated with
  only the values changed.
- **Cyber dashboard:** mono labels, pill chips, fake terminal panels, luminous
  borders everywhere.
- **Corporate AI template:** abstract network image, gradient headline,
  "future of" subtitle, three benefit cards.
- **Brand-color wallpaper:** the brand color is pasted onto every border,
  chip, icon, and heading with no hierarchy.
- **Muddy color wash:** low-saturation blue/green/gray gradients, translucent
  white fog over dark slides, gray text on colored panels, and accents that
  become dull blocks instead of crisp signals. This reads unfinished and makes
  screenshots feel dirty even when the layout is structurally correct.
- **First-slide-as-content-slide:** the cover uses the same two-column, card
  grid, memo panel, or diagram skeleton as the rest of the deck. The first
  slide should feel like an opening image, poster, book cover, title sequence,
  product reveal, or exhibition entrance, not merely slide 1 of the template.
- **Centered grid hero:** centered title, dark grid background, tiny brand chip,
  generic subtitle, and no strong image, material, or editorial idea.

Do not fix these by adding more effects. Fix them by changing the concept,
composition, typography, image strategy, and narrative structure.

## Typography

Choose type from the brief:

- The user's requested aesthetic style must change the type system. Do not keep
  the same display/body pairing when the user moves between luxury, brutalist,
  playful, academic, editorial, operational, cinematic, or other named styles.
- A display face should express the deck's voice: archival, engineered,
  elegant, raw, technical, literary, playful, institutional, etc.
- A body face should remain readable at slide distance and support dense
  captions, lists, or source notes.
- A mono face is useful for code, financial tables, technical labels, and
  operational data only when that language belongs to the deck.

Avoid relying on default or overused pairings out of habit. A common font can be
acceptable only when the surrounding system is intentionally restrained and the
typography is handled with care. Do not pick fonts from a fixed allowed list;
pick them because they fit the concept.

Using the same generic UI font for display and body text is rarely enough for an
Auto deck. If you choose that restraint, the composition, imagery, and editorial
system must carry a very specific point of view.

Define a type hierarchy contract before writing CSS:

- Display: the voice of the deck; large enough and distinctive enough to lead.
- Body: readable at slide distance; not a smaller clone of the display role.
- Caption/source: quiet but legible; never the same emphasis as body copy.
- Data: numbers, units, and labels sized from the container they occupy.
- Labels/chips: navigation or grouping; not decorative confetti.

The type contract must translate style into concrete choices:

- Name the intended font character, not just a family name: high-contrast serif,
  humanist sans, grotesque, slab, rounded sans, condensed editorial display,
  monospaced technical label, calligraphic accent, or another precise voice.
- Pick CSS font stacks that can plausibly render in a self-contained deck.
  Remote font imports are not available; use system and installed-family stacks,
  with sensible fallbacks.
- Adjust weight, case, line height, tracking, numeral treatment, and heading
  scale to fit the chosen style. A font-family swap without hierarchy changes
  is usually not enough.
- Respect the presentation language and script. For CJK decks, use CJK-capable
  display/body stacks and tune line-height, weight, and character count instead
  of applying a Latin display-font idea to Chinese or Japanese headings. For
  multilingual decks, choose compatible stacks and avoid mixing fonts that make
  scripts feel unrelated.
- Match the audience and content burden. Investor, technical, classroom,
  luxury, and playful decks need different body readability, label density,
  numeral emphasis, and heading rhythm even when they share a visual style.

For technology or company decks, avoid defaulting to the common "Inter or system
UI plus JetBrains Mono" pairing. It can work only when the surrounding editorial
system is genuinely specific and final QA proves hierarchy. If the result looks
like a generic dashboard, change the type system, not just the colors.

## Content Budget

Most rough decks fail because each slide is treated as a page of notes rather
than a composed viewport. Before writing slide HTML, decide what each slide is
allowed to hold.

A normal slide should have:

- One focal element.
- One primary primitive.
- One or two supporting blocks.
- One reserved detail area when needed: caption, source note, legend, rail, or
  sequence marker.

Do not combine a title/subtitle stack, two dense columns, a metric-card row, and
a source note on one slide. That is two slides trying to occupy one viewport.
Split it, turn the metrics into the next slide, or reduce the lists to a single
editorial point.

Good density is intentional. Bad density is when the slide still fits only
because text became small, runtime fit kicked in, or the bottom details are
cropped.

## Image Commitment

When the user requests images, imagery becomes part of the design promise.

- Plan which slides need images before writing those slide fragments.
- Generate or place images before referencing them.
- Use every generated image in the final deck.
- If image generation fails, ask for a no-image fallback instead of silently
  dropping the image layer.

A company, product, or technology deck with no images can still be good, but
only if the art direction deliberately replaces imagery with diagrams, data
teardowns, typographic systems, or another strong visual idea. It should not be
the accidental result of skipping assets.

## Color And Materials

Build color from the visual world:

- Define a dominant field, text colors, one or two accents, and restraint rules.
- Define a color-temperature contract: warm paper, cool blueprint, ink-dark,
  archival neutral, product-bright, etc. Avoid palettes whose main impression
  is simply "grayish" unless a deliberately austere, concrete, or archival
  direction demands it.
- Define the deck's primary tone mode: light or dark. Default to one consistent
  mode across the deck; use inverse-tone slides only as planned story beats with
  clear neighboring context and a visibly different display role, not ordinary
  content slides with swapped colors. `html-contract.md` owns the detailed tone
  contract.
- Say where accent color is allowed: section markers, data emphasis, source
  notes, diagrams, labels, or focal calls.
- Say where accent color is forbidden: decorative borders, every card, every
  chip, every heading, or arbitrary glow.
- A brand color is a signal, not a wallpaper.
- Do not place gray or darker same-hue text on saturated colored badges,
  buttons, or focal labels. Use high-contrast light text on dark accents, or a
  dark ink color on pale tints.
- Avoid full-slide translucent white/gray overlays on dark themes. They often
  desaturate the field into a dirty haze. Use hue-specific radial light,
  localized paper grain, or a planned material texture instead.
- Each accent color needs a contrast job: route, state, chapter, risk, product
  surface, or focal call. If an accent looks like a random colored rectangle,
  change either the color or the component role.
- Depth can come from whitespace, image crops, paper grain, rules, diagrams,
  physical surfaces, data density, or layered atmosphere. Gradients and glows
  are optional tools, not proof of quality.

### Palette Hygiene Review

Before finalizing CSS, inspect the cover, at least two ordinary slides in the
primary tone, and every planned inverse-tone or accent slide. Ask:

- Does the dominant field have a clear hue/temperature, or does it read as gray
  fog?
- Are large translucent overlays making the slide look washed out?
- Are focal colored blocks crisp enough to feel intentional?
- Do title, body, source note, and badge colors all have enough contrast?
- Would the screenshot still look clean when scaled down in the overview grid?

If the answer is no, revise the palette before changing layout. Gray haze is a
color-system bug, not a layout bug.

## Cover As Opening Image

The cover is the deck's first-viewport promise. It must be visually distinct
from ordinary evidence/content slides while still belonging to the same world.

Rules:
- Treat slide 1 as a display composition, not a normal information layout.
- It may use a hero wordmark, oversized title, full-bleed product/object/image
  when justified, strong typographic crop, dramatic whitespace, or one memorable
  material surface.
- The cover title should feel like a poster line: short, memorable, and
  non-sentence-like. Put explanatory scope in a small subtitle, chips, or the
  first content slide; see `html-contract.md` for the verifiable copy limits.
- Default to a no-image cover. The safest high-end cover is a premium
  minimalist CSS material field: restrained gradients, subtle pattern or
  texture, strong typography, and generous whitespace. It must look grand,
  simple, and high-end in the first second, not like a generated image was
  placed behind text.
- Decorative layers may frame the hero, but must not cross or compete with the
  title block. Use the Cover Text Safety Zone in `layout-guide.md` whenever the
  cover includes linework, traces, nodes, particles, or pseudo-diagrams.
- Use a cover background/subject image only when the user explicitly asks for
  cover imagery or the topic requires a recognizable product/place/object on
  slide 1.
- It should have fewer content regions than normal slides. Avoid rows of
  repeated cards, dense tables, memo grids, or a balanced two-column evidence
  layout on the cover.
- For company, product, AI, infrastructure, SaaS, and developer-tool decks,
  default to title/wordmark, one terse subtitle, at most 1-3 labels/chips, and
  simple non-text decoration. Do not put labeled process flows, mini
  architecture diagrams, card rows, request pipelines, or explanatory nodes on
  the cover; move that working model to slide 2 or later.
- If the user explicitly asks for a diagram-first cover, make it iconic and
  poster-like: a single symbolic shape with no paragraphs, no tiny node labels,
  and no pale-card/pale-text combinations. It should be understood as a cover
  image, not read as an operational diagram.
- It must look recognizably different from slide 2 in thumbnail view: different
  scale, hierarchy, density, and focal object.
- The cover can share one Magic Move element with slide 2, such as the title,
  logo, or key phrase, but the rest of the composition should transform into the
  deck's working system rather than remain the same layout.

If slide 1 and slide 2 could swap positions without anyone noticing, the cover
has failed.

## Spatial Composition

Every slide still needs a reliable primary layout primitive from
`layout-guide.md`, but the visible composition should follow the art direction.

Use variation with purpose:

- Vary scale: hero, detail, comparison, index, quote, diagram, timeline.
- Vary density: quiet anchor slides, denser evidence slides, focused detail
  slides.
- Vary hierarchy: sometimes the image leads, sometimes the data leads,
  sometimes a phrase or diagram leads.
- Avoid three consecutive slides with the same visible skeleton unless the
  repetition is a deliberate sequence.

## Design Review

Aesthetic quality is subjective and must not be judged by static scripts,
selector counts, color counts, or gradient counts.

Use tools only for objective checks: HTML structure, JavaScript syntax, image
loading, text overflow, viewport fit, and Magic Move continuity.

For subjective quality, do a visual review of rendered slides:

1. Inspect the cover plus several representative slides before generating the
   whole deck when possible. The review must be based on rendered output, not
   just reading the HTML source.
2. Ask: does this look like a real deck for this topic, or could the topic name
   be swapped with another company or idea?
3. Ask: is the most memorable element a real visual idea, or just glow,
   gradients, cards, and big numbers?
4. Ask: did the deck obey its own forbidden tropes?
5. If it feels generic, revise the art direction first, then rewrite CSS and
   representative slides.

The goal is not to pass a checklist. The goal is a deck with a specific visual
world, a clear story, and details that feel intentionally chosen.

# Magic Slide

Magic Slide is a toolkit for building polished, self-contained HTML presentations
with Keynote-style Magic Move transitions, integrated PipeLLM image generation,
and high-quality web search for research-backed decks.

It is designed for presentations that need to feel intentional rather than
template-driven: narrative outlines, distinctive visual systems, smooth motion,
editable source files, and a portable final HTML deck.

## Highlights

### Magic Move Transitions

Magic Slide uses a FLIP-based runtime to animate shared elements between slides.
When titles, cards, metrics, labels, diagrams, or images reappear across adjacent
slides, they can glide, resize, fade, and settle into the next composition
instead of hard-cutting.

Good use cases include:

- Overview-to-detail flows
- Agenda items expanding into section headers
- Cards moving from grids into focused detail slides
- Reused metrics or labels carrying continuity across a story
- Diagram nodes staying visually connected while the explanation changes

### PipeLLM Image Generation

The project includes `scripts/generate-image.py`, a PipeLLM-powered image
generation helper for creating presentation assets on demand. Generated images
can be used as cover atmospheres, content illustrations, product-style visuals,
or replaceable placeholders inside the deck.

Image generation is optional. When a deck does not use generated images, the
visual system should still be rich: typography, CSS diagrams, data treatments,
simple geometric systems, and reliable inline SVG can replace image-heavy
layouts.

### PipeLLM Web Search

The project includes `scripts/websearch.py` for PipeLLM-backed web research. It
is intended for decks where current facts, market context, product details, or
source-backed claims matter.

The search path is treated as a first-class part of deck quality: use it to
sharpen the thesis, improve evidence slides, and avoid generic summaries. Search
results should be converted into a clear argument, not pasted into slides as a
raw fact dump.

### Self-Contained HTML Output

The final presentation is a single HTML file with runtime, styles, slide markup,
and local assets embedded or referenced through the build pipeline. It can be
shared, archived, and presented without a framework-specific runtime.

### Editable Source Workflow

Decks are generated from modular source files:

- `sources/outline.md` keeps the approved narrative plan
- `sources/style.css` contains the deck visual system
- `sources/slide-XX.html` files contain individual slide fragments
- `index.html` is the final merged, runtime-injected presentation

This keeps iteration practical: edit one slide or the shared CSS, rebuild, and
preview again.

## Project Structure

```text
magic-slide-skill/
├── README.md
├── SKILL.md
├── scripts/
│   ├── extract-slides.py
│   ├── generate-image.py
│   ├── inject-runtime.py
│   ├── merge-slides.py
│   ├── serve.py
│   └── websearch.py
└── references/
    ├── design-system.md
    ├── flip-engine.md
    ├── generation-guide.md
    ├── html-contract.md
    ├── images.md
    ├── layout-guide.md
    ├── layouts/
    │   └── primitives.md
    └── workflows/
        ├── step-01-requirements.md
        ├── step-02-websearch.md
        ├── step-03-outline.md
        ├── step-04-design-brief.md
        ├── step-05-prototype.md
        ├── step-06-visual-gate.md
        ├── step-07-generate.md
        ├── step-08-merge.md
        ├── step-09-inject.md
        └── step-10-preview.md
```

Generated decks use this structure:

```text
{topic}/
├── index.html
├── assets/
│   └── image-1.png
└── sources/
    ├── outline.md
    ├── style.css
    ├── slide-01.html
    ├── slide-02.html
    └── qa/
```

The topic root is reserved for deliverables. Process files stay inside
`sources/`.

## Generation Workflow

1. Gather requirements: topic, visual direction, language, and whether generated
   images should be used.
2. Optionally run PipeLLM web search when the deck needs fresh or source-backed
   information.
3. Create an outline with a clear audience, thesis spine, chapter arc, and
   closing idea.
4. Write a compact design brief before producing CSS or slide HTML.
5. Generate `style.css` and the individual slide fragments.
6. Merge slide fragments into `index.html`.
7. Inject the Magic Move runtime and editing helpers.
8. Launch the preview server and fix objective issues such as overflow, broken
   images, SVG artifacts, and transition problems.

## Core Scripts

### Merge slide sources

```bash
python3 scripts/merge-slides.py ./my-deck/sources --lang en
```

Combines `style.css` and `slide-XX.html` fragments into a deck HTML file.

### Inject runtime

```bash
python3 scripts/inject-runtime.py ./my-deck/index.html
```

Adds the presentation runtime, navigation, overview mode, edit mode, progress
state, image upload support, and Magic Move transition engine.

### Preview a deck

```bash
python3 scripts/serve.py ./my-deck/index.html
```

Starts the Magic Slide preview server. Use this server for preview and editing;
it supports features that direct file opening and generic static servers do not.

### Generate an image with PipeLLM

```bash
python3 scripts/generate-image.py "minimal abstract editorial cover texture" \
  --aspect 16:9 \
  --output ./my-deck/assets/cover.png
```

### Search with PipeLLM

```bash
python3 scripts/websearch.py "latest market data for renewable energy storage"
```

## Configuration

PipeLLM features require an API key. Set one of:

```bash
export PIPELLM_API_KEY="your-key"
```

or store the key at:

```text
~/.config/pipellm/api_key
```

Core merging, runtime injection, and preview features only require Python 3 and
a modern browser.

## Design Principles

The design layer integrates principles from Anthropic's official
`frontend-design` skill to guide visual direction, typography, composition,
color depth, and anti-generic quality checks.

- Start with an argument, not a topic inventory.
- Make slide 1 a distinct cover moment, not an ordinary content layout.
- Use Magic Move for meaningful continuity, not decoration.
- Treat generated images as part of the design promise when they are requested.
- When images are not used, replace them deliberately with diagrams, data,
  typography, and geometric systems.
- Prefer reliable HTML/CSS diagrams and simple SVG over fragile decorative
  effects.
- Keep source files modular so decks remain easy to revise.

## Quality Checklist

Before delivery, verify:

- Slides render without errors.
- Text does not overflow or overlap.
- Slide backgrounds cover the full viewport.
- Magic Move transitions are smooth and semantically meaningful.
- Images load correctly when used.
- Inline SVG connectors do not render as filled black shapes.
- Navigation, overview mode, progress, and edit mode work in the preview server.
- The deck has a specific visual world that could not be reused unchanged for a
  completely different topic.

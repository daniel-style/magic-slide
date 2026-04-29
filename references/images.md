# Image Integration Guide

CSS patterns for embedding generated images into slides — both background atmospheric images and content informational images.

## Injected CSS defaults (from inject-runtime.py)

These CSS rules are injected automatically. Deck sources can override them with inline styles when needed.

| CSS class | Injected default | Purpose |
|-----------|-----------------|----------------------------------------|
| `.bg::after` (normal slides) | `linear-gradient(to right, rgba(0,0,0,0.90) → 0.05)` | **Image treatment** |
| `.bg::after` (`.slide-center`) | `radial-gradient(ellipse at center, rgba(0,0,0,0.25) → 0.65)` | **Image treatment** |
| `.img-fade-right` | `mask-image: linear-gradient(to right, #000 70%, transparent)` | **Image treatment** |
| `.img-fade-bottom` | `mask-image: linear-gradient(to bottom, #000 75%, transparent)` | **Image treatment** |
| `.img-fade-all` | `mask-image: radial-gradient(ellipse, #000 50%, transparent 80%)` | **Image treatment** |
| `.avatar` | `120×120px, border-radius:50%, border:3px solid var(--accent)` | **Image treatment** + **Edge treatment** |

To override: use inline `style` on the element or a `<style>` block in the skeleton.

## Background images — opt-in atmosphere behind text

**CRITICAL RULE: Default to no background images.** Cover slides should normally
use a premium minimalist CSS material field instead: restrained gradients,
subtle pattern or texture, strong typography, and generous whitespace. It must
read as grand, calm, simple, and high-end at first glance.

Background images are allowed only in narrow cases:
- The user explicitly asks for cover imagery or photographic/generated cover
  art.
- The topic requires a recognizable product, place, or object on slide 1.
- A closing slide explicitly needs a visual background.

All middle content slides use solid colors, CSS gradients, diagrams, or content
images only. Never add background images to middle slides.

```html
<div class="bg" style="background-image:url('./[topic]-assets/slide-N-bg.png')"></div>
<div style="position:relative;z-index:1">...slide content...</div>
```

The `.bg::after` overlay gradient is injected by default. Text always sits on the dark side. Deck sources can customize the overlay via inline style on `.bg` when needed (e.g. stronger overlay for darker themes, softer for lighter ones).

Do not implement the apparent cover background as an uploadable image wrapper,
inset panel, or document-flow image. If a cover background image is explicitly
allowed, it must be owned by the root `.slide` background or a full-bleed
absolutely positioned decorative layer behind `.slide-content`.

**Background prompts must produce purely abstract, texture-only images — no recognisable objects, no readable text, no detailed illustrations.** The image will be covered by a dark gradient overlay and slide text; any content in the image will compete with and obscure the text.

### Cover slide backgrounds (special requirements)

**Cover slide background images are not the default.** Use them only when the
user explicitly requested cover imagery or the topic requires a recognizable
cover subject. Otherwise, create the cover with CSS gradients, pattern, texture,
typography, and whitespace.

When a cover background image is allowed, it must be subtle and understated,
creating visual impact without overwhelming the title. The goal is restrained
elegance with just enough visual interest to elevate the design. **Background
images must be low-key and sophisticated — never busy or distracting. The title
is the hero, not the background.**

**Cover background formula:**
```
"minimal abstract [color palette] gradient, [subtle texture: soft grain / faint geometric pattern / delicate light rays / gentle bokeh], very dark background, extremely subtle, refined, elegant, understated, no objects, no text"
```

**Key principles for cover backgrounds:**
- **Minimal complexity**: Single gradient or very simple geometric pattern only
- **Low contrast**: Subtle color shifts, never harsh transitions
- **Dark foundation**: Must be predominantly dark (80%+ black/near-black) so white text pops
- **Refined texture**: Grain, soft bokeh, or faint geometric lines — nothing busy or distracting
- **Accent color integration**: Use the brand's accent color sparingly (10-20% of the composition, very desaturated)

**Examples of good cover background prompts:**
- Tech/corporate: `"minimal dark charcoal to black gradient, faint vertical light streaks, subtle grain texture, extremely refined, no objects no text"`
- Creative/bold: `"dark navy to black radial gradient, soft [accent color] glow in corner, delicate bokeh particles, very subtle, no objects no text"`
- Professional/elegant: `"deep black background, minimal geometric grid pattern barely visible, soft ambient lighting, extremely understated, no objects no text"`

**Anti-patterns for cover backgrounds (avoid these):**
- Busy patterns, complex shapes, multiple gradients
- Bright colors, high contrast, saturated hues
- Recognizable objects, icons, symbols, text
- Photographic elements, realistic textures
- Anything that competes with the title text for attention

## Cover subject images — must read as intentional hero art

If the cover uses a real or generated subject image instead of an abstract
background, the image treatment must feel like a deliberate cover composition.
Never place a narrow cropped strip, accidental product slice, anonymous hardware
edge, or arbitrary object fragment beside the title. A viewer should understand
why that image is on the cover within one second.

Allowed cover image treatments:
- Full-bleed image with a strong overlay and text on the quiet side.
- Wide hero panel, usually `16:9`, `4:3`, or a deliberate panoramic crop, where
  the subject remains readable.
- Large isolated object/product crop with the important object mostly visible,
  not a thin vertical slice.
- Abstract material field generated specifically for the cover, with no
  recognizable subject competing with the title.

Avoid:
- Tall narrow image columns created by putting a landscape image into a skinny
  `height:70vh` container with `object-fit:cover`.
- Crops that show only a door edge, server rack sliver, laptop corner, cable
  strip, face fragment, or other low-information slice.
- Raw rectangular photos dropped next to a title without feathering, overlay,
  masking, or a clear relationship to the layout.
- Cover images that overlap the title unless the overlap is the central design
  idea and the text remains fully readable.

Cover image QA:
- Inspect the rendered cover at desktop and mobile sizes.
- If the user did not explicitly request cover imagery and the cover uses a
  generated/photo background anyway, remove the image and replace it with a CSS
  material field before delivery.
- If the subject is cropped so tightly that it reads as a random texture or
  vertical stripe, change the container aspect ratio, use `object-fit:contain`,
  regenerate the image, or remove the image and use a typographic/material
  cover.
- If the cover image looks like an ordinary split-layout content slide, revise
  the cover composition before generating the rest of the deck.

### Content slide backgrounds

**Content slides (all middle slides) NEVER use background images.** Use solid colors or gradients only, defined in `style.css` or inline styles.

For the rare case where a closing slide needs a background image (user explicitly requests it):

**Good background prompt formula:**
```
"abstract [color palette] gradient, [one texture word: bokeh / soft particles / light streaks / mist / noise / ripples], dark background, extremely subtle, understated, elegant, no objects, no text, no figures"
```

**Examples:**
- Closing: `"warm amber to black radial gradient, soft bokeh glow, dark vignette, extremely subtle, no objects no text"`

Never include: code, dashboards, shields, people, logos, architecture diagrams, or any recognisable subject matter in a background image — save those for **content images** instead. Never include readable text or numbers in background images.

## Content images — informational, part of the layout

Content images sit alongside text in split layouts, inside cards, or as standalone visuals. They need proper integration — never a raw rectangle.

### Feathered edges (injected defaults, overridable)

The `.img-fade-right`, `.img-fade-bottom`, `.img-fade-all` classes are injected with the default mask percentages shown in the table above. Adjust fade percentages via inline styles when needed for softer or harder edges.

### Circular clip for avatars / portraits (injected default)

The `.avatar` class is injected at 120×120px with `border-radius:50%` and accent border. Override size and shape via inline styles when needed (e.g. square with rounded corners, larger size, no border).

### Custom clip-path examples (fully customizable — NOT injected)

These are creative ideas that can be adapted freely:
```css
/* Diagonal cut — great for split layouts */
.img-diagonal { clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%); }
/* Rounded rectangle with one organic corner */
.img-blob { clip-path: polygon(0 0, 100% 0, 100% 80%, 85% 100%, 0 100%); border-radius: 0 16px 0 16px; }
```

### Image + text split layout

See `layouts.md` → "Image + text split" for the full grid pattern. Image edge is feathered with the `.img-fade-right` class.

## Content image prompts

Content prompts should be specific and contextual — not atmospheric:
- Describe the **actual subject**: `"minimalist flat illustration of a software architect at a desk, neutral background, 1:1"`
- Include style: `"minimalist flat illustration of..."`, `"isometric diagram of..."`, `"cinematic close-up of..."`
- For person slides, generate at `1:1` aspect and display with appropriate shape (circular, rounded square, etc.)

**Never generate portraits or likenesses of real, living people** — no named individuals, celebrities, public figures, or anyone recognisable. Use illustrated or abstract representations instead (e.g. `"flat illustration of a developer silhouette"`, `"abstract avatar icon"`, `"isometric figure at a workstation"`). This avoids rights issues and AI image policy violations.

## Decorative text in images

Including topic keywords in generated images makes them feel intentional:
- Cover slide about LangChain: `"with stylized text 'LANGCHAIN' subtly embedded in the composition"`
- Architecture slide: `"background with faint blueprint-style technical annotations"`
- Timeline slide: `"with year numbers '2024' '2025' floating in the background"`

## Uploadable image placeholders

**CRITICAL: ALL `<img>` elements in slides MUST use the uploadable-wrap structure** — whether they're AI-generated placeholders, real photos, or any other image. This allows users to replace any image in edit mode.

When a slide features a real person (founder, CEO, speaker, etc.):

1. **First generate an AI placeholder** using `generate-image.py` with a stylized/illustrative prompt (never a real likeness)
2. **Use it as the default `src`** in the `<img>` tag so the slide looks good immediately
3. **Wrap it in `uploadable-wrap`** so the user can hover and upload a real photo to replace it at any time

For non-person images (products, diagrams, illustrations):
1. **Generate the image** using `generate-image.py` with appropriate prompt
2. **Wrap it in `uploadable-wrap`** so the user can replace it if needed

### Step 1: Generate the placeholder/image

```bash
python3 <magic-slide-path>/scripts/generate-image.py \
  "stylized illustration portrait, [role description], dark background, [accent color] lighting, abstract artistic style, no face details, cinematic" \
  --aspect 1:1 --output ./[topic]-assets/[person-id]-placeholder.png
```

Prompt guidelines for person placeholders:
- Always abstract/illustrative — never photorealistic, never a named person's likeness
- Include the role context: "tech CEO", "scientist", "engineer"
- Match the deck's color theme in the lighting description
- Add: "no face details, silhouette-inspired, artistic, cinematic"

### Step 2: HTML markup

**REQUIRED structure for ALL images** (adapt visual styles as needed, but keep structural attributes exactly):

```html
<div class="uploadable-wrap" style="width:280px;height:280px;border-radius:50%;overflow:hidden;position:relative">
  <!-- Image with data-uploadable attribute -->
  <img src="[topic]-assets/image-name.png" alt="Description" 
       data-uploadable="unique-id"
       style="width:100%;height:100%;object-fit:cover">
  
  <!-- Upload button (hidden by default, shown on hover in edit mode) -->
  <button class="upload-btn" 
          onclick="document.getElementById('upload-unique-id').click()"
          style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                 background:rgba(118,185,0,0.9);color:#fff;border:none;
                 padding:12px 24px;border-radius:8px;cursor:pointer;
                 font-size:0.9rem;font-weight:600;opacity:0;transition:opacity 0.3s;
                 pointer-events:auto">
    📁 Upload Image
  </button>
  
  <!-- Hidden file input -->
  <input type="file" id="upload-unique-id" accept="image/*" 
         onchange="msHandleImageUpload(this,'unique-id')" 
         style="display:none">
</div>
```

**For split-layout images (16:9 aspect):**
```html
<div class="uploadable-wrap" style="width:100%;max-width:none;aspect-ratio:16/9;overflow:hidden;position:relative">
  <img src="[topic]-assets/image-name.png" alt="Description"
       data-uploadable="unique-id"
       style="width:100%;height:100%;object-fit:cover;border-radius:8px">
  <button class="upload-btn" onclick="document.getElementById('upload-unique-id').click()"
          style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                 background:rgba(118,185,0,0.9);color:#fff;border:none;
                 padding:12px 24px;border-radius:8px;cursor:pointer;
                 font-size:0.9rem;font-weight:600;opacity:0;transition:opacity 0.3s;
                 pointer-events:auto">📁 Upload Image</button>
  <input type="file" id="upload-unique-id" accept="image/*"
         onchange="msHandleImageUpload(this,'unique-id')" style="display:none">
</div>
```

**For portrait images (3:4 aspect):**
```html
<div class="uploadable-wrap" style="width:100%;max-width:400px;aspect-ratio:3/4;overflow:hidden;position:relative">
  <img src="[topic]-assets/image-name.png" alt="Description"
       data-uploadable="unique-id"
       style="width:100%;height:100%;object-fit:cover;border-radius:8px">
  <button class="upload-btn" onclick="document.getElementById('upload-unique-id').click()"
          style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                 background:rgba(118,185,0,0.9);color:#fff;border:none;
                 padding:12px 24px;border-radius:8px;cursor:pointer;
                 font-size:0.9rem;font-weight:600;opacity:0;transition:opacity 0.3s;
                 pointer-events:auto">📁 Upload Image</button>
  <input type="file" id="upload-unique-id" accept="image/*"
         onchange="msHandleImageUpload(this,'unique-id')" style="display:none">
</div>
```

**Rules:**
- `data-uploadable` value must be unique per deck (e.g. `"jensen"`, `"cto"`, `"product-1"`)
- `id="upload-{same-id}"` on the input must match the button's `onclick` target
- `onchange` must call `msHandleImageUpload(this, 'same-id-as-data-uploadable')`
- Button text can be localized but structure must stay the same
- `overflow:hidden` on wrapper is required for `object-fit:cover` to work
- `position:relative` on wrapper is required for absolute-positioned button

**The upload button is hidden by default (`opacity:0`) and shown on hover via CSS injected by `inject-runtime.py`.** In edit mode, hovering over any `uploadable-wrap` reveals the button.

---

## Rules

- Never place a sharp-edged rectangular image directly on a slide without feathering or clipping
- Never use an unrelated stock-photo-style image — every image should visually echo the slide's topic
- Never use the same prompt style for background and content images — backgrounds are atmospheric, content images are specific
- All visual treatment of images (overlay strength, fade percentages, portrait shape) should be chosen based on the slide's design needs

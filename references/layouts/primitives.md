# Layout Primitives - Detailed HTML Structures

This document provides detailed HTML structure and code examples for each layout primitive.

For layout principles and guidelines, see [layout-guide.md](../layout-guide.md).

## Available Primitives

### 1. Cover Slide (Title Slide)

**Structure:**
```html
<section class="slide" data-id="cover" data-transition="scale-in" data-stagger="zoom-in" data-bg="dark">
  <div class="slide-content">
    <h1 style="font-size: clamp(3rem, 6vw, 6rem); margin-bottom: 1rem; text-align: center;">
      Main Title
    </h1>
    <p style="font-size: clamp(1rem, 1.8vw, 2rem); opacity: 0.7; text-align: center;">
      Subtitle or description
    </p>
  </div>
</section>
```

**Key points:**
- Large title (3-5rem)
- Centered text
- Optional subtitle
- Minimal content

### 2. Section Header Slide

**Structure:**
```html
<section class="slide" data-id="section-1" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content">
    <h2 style="font-size: clamp(2rem, 4vw, 4rem); text-align: center;">
      Section Title
    </h2>
  </div>
</section>
```

**Key points:**
- Single large heading
- Can be centered, left-aligned, or edge-aligned depending on the deck language
- No other content

### 3. Content Slide (Text + List)

**Structure:**
```html
<section class="slide" data-id="content-1" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content">
    <h2 style="font-size: clamp(1.8rem, 3vw, 3.5rem); margin-bottom: clamp(1.5rem, 3vw, 3rem); align-self: flex-start;">
      Slide Title
    </h2>
    <ul style="font-size: clamp(1rem, 1.15vw, 1.3rem); line-height: 1.7; align-self: flex-start; max-width: 800px;">
      <li>First point</li>
      <li>Second point</li>
      <li>Third point</li>
    </ul>
  </div>
</section>
```

**Key points:**
- Title at top (align-self: flex-start)
- List below title
- Reasonable font sizes: body is readable but clearly below hero scale
- Max-width to prevent text from being too wide

### 4. Two-Column Layout

**Structure:**
```html
<section class="slide" data-id="two-col" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content">
    <h2 style="font-size: 2.5rem; margin-bottom: 2rem; align-self: flex-start;">
      Slide Title
    </h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; width: 100%;">
      <div>
        <h3 style="font-size: 1.8rem; margin-bottom: 1rem;">Left Column</h3>
        <p style="font-size: 1.2rem; line-height: 1.6;">Content here</p>
      </div>
      <div>
        <h3 style="font-size: 1.8rem; margin-bottom: 1rem;">Right Column</h3>
        <p style="font-size: 1.2rem; line-height: 1.6;">Content here</p>
      </div>
    </div>
  </div>
</section>
```

**Key points:**
- Use CSS Grid for columns
- Equal width columns (1fr 1fr)
- Adequate gap (2-3rem)
- Consistent font sizes

### 5. Image + Text Slide (Vertical Stack)

**Structure:**
```html
<section class="slide" data-id="image-1" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content">
    <h2 style="font-size: clamp(1.8rem, 3vw, 3.5rem); margin-bottom: clamp(1.5rem, 3vw, 3rem); align-self: flex-start;">
      Slide Title
    </h2>
    <img src="assets/image-1.png" alt="Description" 
         style="max-width: 600px; max-height: 400px; margin-bottom: 1.5rem; border-radius: 0.5rem;">
    <p style="font-size: clamp(1rem, 1.15vw, 1.3rem); text-align: center; max-width: 700px;">
      Image caption or description
    </p>
  </div>
</section>
```

**Key points:**
- Constrain image size (max-width, max-height)
- Add border-radius for polish
- Caption below image
- Center caption text

### 6. Image + Text Slide (Horizontal Split)

**CRITICAL: Use this pattern when you have an image and substantial text content side-by-side.**

**Structure:**
```html
<section class="slide" data-id="image-text" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content" style="flex-direction: row; align-items: center; gap: clamp(2rem, 4vw, 4rem);">
    <!-- Left: Image -->
    <div style="flex: 0 0 45%; display: flex; justify-content: center; align-items: center;">
      <img src="assets/image-1.png" alt="Description" 
           style="max-width: 100%; height: auto; border-radius: 0.5rem;">
    </div>
    
    <!-- Right: Text content -->
    <div style="flex: 1; display: flex; flex-direction: column; gap: clamp(1rem, 2vw, 2rem);">
      <h2 style="font-size: clamp(2rem, 4vw, 4rem); line-height: 1.2;">
        The 81-Point Game
      </h2>
      <h3 style="font-size: clamp(3rem, 6vw, 6rem); font-weight: 900; line-height: 1;">
        81
      </h3>
      <p style="font-size: clamp(1rem, 1.15vw, 1.3rem); line-height: 1.6;">
        On January 22, 2006, Kobe scored 81 points against the Toronto Raptors
      </p>
      <p style="font-size: clamp(0.78rem, 0.9vw, 0.95rem); opacity: 0.7; line-height: 1.6;">
        The second-highest single-game scoring performance in NBA history
      </p>
    </div>
  </div>
</section>
```

**Key points:**
- Override `.slide-content` with `flex-direction: row` (inline style)
- Left side: Fixed width (45%) for image container
- Right side: Flexible width (`flex: 1`) for text content
- Use `gap` for spacing between columns (not margin)
- Image container uses flexbox centering
- Text content stacked vertically with internal gaps
- **NEVER leave one side empty** — always balance content

**Why this works:**
- `flex: 0 0 45%` — Image takes exactly 45% width, doesn't grow/shrink
- `flex: 1` — Text takes remaining space (55% minus gap)
- `gap: clamp(2rem, 4vw, 4rem)` — Responsive spacing between columns
- Both sides have content, preventing the "empty left, crowded right" problem

**Reliability guardrails:**
- Default to `align-items: center` or `align-items: flex-start/start`, not equal-height stretching.
- If the media keeps its own `aspect-ratio`, its wrapper should hug the media's natural height rather than fill the sibling column.
- If one column becomes mostly empty structural space instead of intentional negative space, this layout choice is wrong. Switch to a vertical stack or split into two slides.
- Use horizontal split only when both sides carry substantial, balanced content.

### 7. Code Slide

**Structure:**
```html
<section class="slide" data-id="code-1" data-transition="fade" data-stagger="cascade" data-bg="dark">
  <div class="slide-content">
    <h2 style="font-size: 2.5rem; margin-bottom: 2rem; align-self: flex-start;">
      Code Example
    </h2>
    <pre style="background: rgba(0,0,0,0.3); padding: 2rem; border-radius: 0.5rem; font-size: 1.2rem; max-width: 900px; overflow-x: auto;"><code>function example() {
  return "Hello World";
}</code></pre>
  </div>
</section>
```

**Key points:**
- Use `<pre><code>` for code blocks
- Dark background for contrast
- Adequate padding
- Monospace font (inherited)
- Overflow handling


## Step 8: Preview & Final QA

### 10a. Launch preview

This step is mandatory. Do not skip it after generating or updating a deck.
The presentation's edit mode, Save button, image replacement, and close/shutdown
controls depend on the Magic Slide preview server. Opening `index.html` directly
or using a generic static server is not an acceptable substitute.

```bash
# Find skill directory
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)

# Start preview server (MUST use this script)
python3 "$SKILL_DIR/scripts/serve.py" {topic}/index.html
```

Keep this command running while the user previews or edits the deck. If the
command prints an existing service URL instead of starting a new foreground
process, use that URL. If the command fails because the skill directory was not
found, locate `magic-slide-skill` manually and re-run the same `serve.py` script
with an absolute path.

### 10b. Final QA checklist

**Objective checks:**
1. All slides render without errors
2. No content overflow on any slide
3. Root slide backgrounds cover the whole viewport in normal view and overview thumbnails
4. Slide 1 reads as a distinct cover/opening image, not the same skeleton as slide 2
5. Palette does not look gray, foggy, or washed out in the cover, one light slide, one dark slide, and one accent slide
6. Accent blocks/badges have clear foreground contrast and do not use dark same-hue text on saturated color
7. Sparse slides are vertically centered unless deliberately dense/top-aligned
8. No headings, cards, diagrams, or source notes overlap
9. Inline SVG diagrams have no black filled connector blobs
10. Magic Move transitions work smoothly
11. All images load correctly
12. Navigation works (arrows, space, click)
13. Progress bar updates correctly
14. Slide counter shows correct numbers
15. Edit mode works (press 'e')

**Subjective review:**
- Visual consistency across all slides
- Clear hierarchy and readability
- Distinctive aesthetic (not generic)
- Strong cover: simple, spacious, memorable, and visibly different from
  ordinary content slides
- Clean palette: no muddy gray wash, accidental fog overlay, or weak accent
  block
- Smooth pacing and flow
- Strong opening and closing

### 10c. Deliver to user

Tell the user:
- Preview is running at the displayed URL from `scripts/serve.py`
- Final HTML is at `{topic}/index.html`
- Final assets, if any, are in `{topic}/assets/`
- They can edit sources in `{topic}/sources/` and re-run merge/inject
- Process files such as outline, helper scripts, and QA artifacts are kept in
  `{topic}/sources/` so the topic root contains only deliverables
- They can use edit mode (press 'e') for quick text changes while the preview server is running
- The HTML file is self-contained and portable

## Post-Generation Editing

Users can edit the presentation in two ways:

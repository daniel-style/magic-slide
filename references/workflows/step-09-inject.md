## Step 7: Inject Runtime

Add the FLIP engine, navigation, and interactive features:

```bash
# Find skill directory
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)

# Inject runtime
python3 "$SKILL_DIR/scripts/inject-runtime.py" {topic}/index.html --lang {language}
```

Hard boundary:
- Treat `scripts/inject-runtime.py` and the behavior/results it injects into
  the finished deck as Magic Slide runtime output.
- Preserve injected behavior by default. Do not edit the injector, patch
  injected runtime blocks in `{topic}/index.html`, or add source CSS/HTML/JS
  that disables, hides, neutralizes, or overrides injected features unless the
  user explicitly asks for that specific runtime behavior change.
- Prohibited "cleanup" without explicit user request includes hiding the
  animated/custom cursor, restoring the system cursor with `cursor: auto` or
  `cursor: default`, removing or hiding navigation/progress/edit controls,
  turning off Magic Move, suppressing injected stagger, or bypassing runtime fit.
- Fix deck-specific issues in `sources/style.css` and `sources/slide-XX.html`
  around the runtime behavior, then re-run merge and this unchanged injection
  step. If the issue appears to be caused by injected runtime behavior itself,
  report it or ask before changing it.

This injects:
- FLIP animation engine
- Keyboard navigation (arrow keys, space)
- Progress bar
- Slide counter
- Edit mode (press 'e')
- Stagger animations for list items

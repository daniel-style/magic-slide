## Optional: Build Visual Prototype

Use this optional checkpoint only when the user asks to see a sample before the
full deck or when a risky visual direction needs approval. The default workflow
generates the production deck directly after outline confirmation.

### Select Prototype Slides

Choose 3-5 slides from the outline that represent different risks:
- Cover or opening thesis
- Dense content or comparison
- Diagram/image/data slide
- Section transition or closing

### Generate Prototype Files

Create only the selected `{topic}/sources/slide-XX.html` files plus
`{topic}/sources/style.css`. Follow:
- `html-contract.md` for structure, deck tone mode, root backgrounds, and SVG rules
- `layout-guide.md` for fit, centering, and overlap rules
- `flip-engine.md` for Magic Move rules
- Brief Lite

### Merge And Inject Prototype

```bash
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)
python3 "$SKILL_DIR/scripts/merge-slides.py" {topic}/sources/ --lang {language}
python3 "$SKILL_DIR/scripts/inject-runtime.py" {topic}/index.html --lang {language}
```

### Launch Preview

```bash
python3 "$SKILL_DIR/scripts/serve.py" {topic}/index.html
```

After prototype approval, continue with `step-07-generate.md` for the full
production source pass.

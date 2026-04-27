## Step 6: Merge Slides

Combine all modular slide files into a single HTML file:

```bash
# Find skill directory
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)

# Merge all slides
python3 "$SKILL_DIR/scripts/merge-slides.py" {topic}/sources/ --lang {language}
```

This creates `{topic}/index.html` with all slides combined.

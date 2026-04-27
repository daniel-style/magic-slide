## Step 7: Inject Runtime

Add the FLIP engine, navigation, and interactive features:

```bash
# Find skill directory
SKILL_DIR=$(find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1)

# Inject runtime
python3 "$SKILL_DIR/scripts/inject-runtime.py" {topic}/index.html --lang {language}
```

This injects:
- FLIP animation engine
- Keyboard navigation (arrow keys, space)
- Progress bar
- Slide counter
- Edit mode (press 'e')
- Stagger animations for list items

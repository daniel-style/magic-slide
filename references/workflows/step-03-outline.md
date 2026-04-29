## Step 3: Generate Outline (REQUIRED — Cannot Skip)

**CRITICAL:** You MUST generate an outline and get user confirmation before proceeding to Step 4. This step cannot be skipped.

### 3a. Generate the outline

Create `{topic}/sources/outline.md` with this structure. The topic root should
remain reserved for final deliverables (`index.html` and `assets/`) plus the
`sources/` directory:

```markdown
# [Presentation Title]

**Target slides:** [requested slide count]
**Audience / lens:** [who this deck is for and how they will judge it] ← REQUIRED, NOT OPTIONAL
**Thesis spine:** [one sentence the deck proves] ← REQUIRED, NOT OPTIONAL
**Chapter arc:** [how the story turns from beginning to end] ← REQUIRED, NOT OPTIONAL
**Closing idea:** [the non-generic idea the final slide should land] ← REQUIRED, NOT OPTIONAL

## Slide 1: [Concise Cover Title]
- Content point 1
- Content point 2

## Slide 2: [Slide Title]
- Content point 1
- Content point 2

...
```

**🛑 MANDATORY OUTLINE REQUIREMENTS:**

1. **Audience / lens** - You MUST specify who the deck is for and how they will judge it. Generic answers like "general audience" are NOT acceptable.

2. **Thesis spine** - You MUST write ONE sentence that the entire deck proves. This is not a topic description. Bad: "This deck is about NVIDIA." Good: "NVIDIA's advantage is a compounding full-stack system, not just faster chips."

3. **Chapter arc** - You MUST describe how the story turns from beginning to end. What changes in the audience's understanding?

4. **Closing idea** - You MUST specify a non-generic idea for the final slide. Bad: "The future is bright." Good: "To understand NVIDIA, stop asking 'which GPU is fastest?' and ask 'who controls the operating system of intelligence infrastructure?'"

5. **Slide 1 title is cover copy** - Keep it short and title-like. Do not use
   the full topic sentence as the cover H1; `html-contract.md` owns the
   detailed cover copy rules.

6. **Each slide must advance the argument** - Not just list information. If a slide only says "this also exists", merge it or sharpen it.

The outline must be an argument, not a topic inventory. For company, technology, finance, or product decks, avoid a flat encyclopedia sequence such as history, products, market, partnerships, future. Each slide should either advance the thesis, provide evidence, create contrast, answer a risk/question, or resolve the story.

### 3b. Confirm with user (REQUIRED)

**CRITICAL:** You MUST use the AskUserQuestion tool for outline confirmation. Text-based interaction is ONLY a fallback if the tool is unavailable.

**Try AskUserQuestion first:**

```python
AskUserQuestion(
    questions=[
        {
            "question": "I've created an outline with X slides. Please review {topic}/sources/outline.md. What would you like to do?",
            "header": "Outline",
            "options": [
                {
                    "label": "Looks good, proceed",
                    "description": "Generate slides based on this outline"
                },
                {
                    "label": "I'll edit it first",
                    "description": "Let me modify sources/outline.md before you generate"
                },
                {
                    "label": "Change something",
                    "description": "Tell me what to adjust"
                }
            ],
            "multiSelect": False
        }
    ]
)
```

### Fallback: Text-based (Only if AskUserQuestion fails)

**ONLY use this if AskUserQuestion tool is not available or fails.**

Show the outline summary in plain text and ask the user to confirm, request
changes, or edit `{topic}/sources/outline.md` directly. Do not include a
copyable response template or example reply for outline confirmation.

Do not proceed to Step 4 until the user explicitly confirms.

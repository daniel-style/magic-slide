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
**Magic Move spine:** [recurring anchors and adjacent transition beats the deck should stage] ← REQUIRED, NOT OPTIONAL

## Slide 1: [Concise Cover Title]
- Content point 1
- Content point 2
- Magic Move candidates: [stable labels/numbers/objects that can carry to Slide 2, or "hard cut"]

## Slide 2: [Slide Title]
- Content point 1
- Content point 2
- Magic Move candidates: [anchors from previous slide and/or anchors carried forward]

...

## Magic Move Storyboard
- Slide 1 -> Slide 2: [anchor text/object] moves from [role] to [role], or "hard cut: [reason]"
- Slide 2 -> Slide 3: [anchor text/object] moves from [role] to [role]
- ...
```

**🛑 MANDATORY OUTLINE REQUIREMENTS:**

1. **Audience / lens** - You MUST specify who the deck is for and how they will judge it. Generic answers like "general audience" are NOT acceptable.

2. **Thesis spine** - You MUST write ONE sentence that the entire deck proves. This is not a topic description. Bad: "This deck is about NVIDIA." Good: "NVIDIA's advantage is a compounding full-stack system, not just faster chips."

3. **Chapter arc** - You MUST describe how the story turns from beginning to end. What changes in the audience's understanding?

4. **Closing idea** - You MUST specify a non-generic idea for the final slide. Bad: "The future is bright." Good: "To understand NVIDIA, stop asking 'which GPU is fastest?' and ask 'who controls the operating system of intelligence infrastructure?'"

5. **Magic Move spine** - You MUST plan Magic Move while the story is still
   malleable. Name recurring anchors such as a short deck mark, chapter labels,
   product/entity names, card titles, key numbers, dates, images, or diagram
   nodes that can persist across adjacent slides. For each natural
   overview/detail, compare/contrast, or chapter sequence, include at least one
   candidate anchor; for intentional scene breaks, write "hard cut" and keep
   the break rare.

6. **Slide-level Magic Move candidates** - Each slide entry should name the
   elements that can enter from the previous slide or carry into the next one.
   These candidates are content planning notes, not final HTML ids, but they
   should already use exact visible text where possible so Step 5 can create
   reliable `data-magic-id` pairs.

7. **Magic Move Storyboard** - Before asking for outline confirmation, include
   a compact adjacent-pair storyboard. This is where you prove the deck has
   enough real continuity before any HTML is written. If the storyboard mostly
   repeats a tiny global deck mark or says "hard cut", change the slide order
   or split/merge slides now.

8. **Slide 1 title is cover copy** - Keep it short and title-like. Do not use
   the full topic sentence as the cover H1; `html-contract.md` owns the
   detailed cover copy rules.

9. **Each slide must advance the argument** - Not just list information. If a slide only says "this also exists", merge it or sharpen it.

The outline must be an argument, not a topic inventory. For company, technology, finance, or product decks, avoid a flat encyclopedia sequence such as history, products, market, partnerships, future. Each slide should either advance the thesis, provide evidence, create contrast, answer a risk/question, or resolve the story.

Magic Move should influence slide order and content grouping. Prefer sequences
like index -> focused detail, small metric -> hero metric, system map -> zoomed
node, or comparison row -> evidence slide. Do not add fake repeated labels just
to animate; instead, arrange the argument so real repeated entities can move.

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

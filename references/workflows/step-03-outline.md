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
**Magic Move spine:** [content relay system: how concepts pass between adjacent slides through primary anchors] ← REQUIRED, NOT OPTIONAL

## Slide 1: [Concise Cover Title]
- Content role: [what this slide proves, sets up, contrasts, or resolves]
- Content point 1
- Content point 2
- Inherited from previous: [none / cover opening / chapter break]
- Passed to next: [concept, label, number, object, card, image, or node that should become the next slide's premise/focus/detail]
- Content relay / Magic Move plan: Primary anchor: [exact visible text/object and role change into next slide, or "hard cut: reason"]; Supporting anchors: [optional exact labels/objects]

## Slide 2: [Slide Title]
- Content role: [what this slide proves, sets up, contrasts, or resolves]
- Content point 1
- Content point 2
- Inherited from previous: [concept/anchor from prior slide and how it becomes this slide's premise/focus/detail]
- Passed to next: [concept/anchor this slide hands forward]
- Content relay / Magic Move plan: Primary anchor: [exact visible text/object and role change from/to adjacent slide, or "hard cut: reason"]; Supporting anchors: [optional exact labels/objects]

...

## Magic Move Storyboard
- Slide 1 -> Slide 2:
  - Content relationship: [continuation / amplification / decomposition / contrast / return / chapter break]
  - Primary anchor: [exact visible text/object] moves from [visual/content role] to [visual/content role], or "hard cut: [content reason]"
  - Supporting anchors: [optional exact labels/objects that reinforce context]
- Slide 2 -> Slide 3:
  - Content relationship: [continuation / amplification / decomposition / contrast / return / chapter break]
  - Primary anchor: [exact visible text/object] moves from [visual/content role] to [visual/content role]
  - Supporting anchors: [optional exact labels/objects]
- ...
```

**🛑 MANDATORY OUTLINE REQUIREMENTS:**

1. **Audience / lens** - You MUST specify who the deck is for and how they will judge it. Generic answers like "general audience" are NOT acceptable.

2. **Thesis spine** - You MUST write ONE sentence that the entire deck proves. This is not a topic description. Bad: "This deck is about NVIDIA." Good: "NVIDIA's advantage is a compounding full-stack system, not just faster chips."

3. **Chapter arc** - You MUST describe how the story turns from beginning to end. What changes in the audience's understanding?

4. **Closing idea** - You MUST specify a non-generic idea for the final slide. Bad: "The future is bright." Good: "To understand NVIDIA, stop asking 'which GPU is fastest?' and ask 'who controls the operating system of intelligence infrastructure?'"

5. **Content-first Magic Move spine** - Plan Magic Move while the story is
   still malleable, but keep content first. For every adjacent pair, decide
   what idea, evidence, object, number, card, image, or diagram node should
   pass forward because it is becoming the next slide's premise, focus, detail,
   contrast, or resolution. Magic Move should shape continuity and slide order;
   it must not distort facts or manufacture fake repeated labels.

   Do not describe the spine as a reusable visual token system, such as
   "rounded pipe tokens", "focus chips", "magic labels", or a recurring bottom
   token row. Those are design devices, not story continuity. The spine should
   name real content objects that would still belong on the slide if Magic Move
   did not exist.

6. **Slide-level content relay fields** - Each slide entry must name its
   content role, what it inherits from the prior slide, what it passes to the
   next slide, and the primary Magic Move anchor when there is continuity.
   These are content planning notes, not final HTML ids, but they should use
   exact visible text where possible so Step 5 can create reliable
   `data-magic-id` pairs.

7. **Primary anchor over small labels** - Each non-hard-cut transition should
   have one primary anchor that is visually meaningful in at least one of the
   two slides: a main card, heading phrase, hero metric, image/object, timeline
   date, comparison row, or diagram node. Small deck marks, footers, corner
   labels, watermarks, pure chapter chips, and invented body labels do not
   satisfy the relay by themselves. Treat them as non-magic by default; use a
   short label as a supporting anchor only when it is already necessary content
   such as a real status, timeline date, card title, or diagram node label. Use
   `flip-engine.md` for the full primary-anchor quality standard.

8. **Magic Move Storyboard** - Before asking for outline confirmation, include
   a compact adjacent-pair storyboard. This is where you prove the deck has
   enough real continuity before any HTML is written. Each pair must name the
   content relationship: continuation, amplification, decomposition, contrast,
   return, or chapter break. If the storyboard mostly repeats a tiny global
   deck mark or says "hard cut", change the slide order or split/merge slides
   now.

9. **Hard cuts are rare content decisions** - Use "hard cut" only for true
   chapter breaks, tone resets, or content shifts where continuity would make
   the argument less clear. Always write the content reason. Do not use hard
   cuts to avoid planning relay opportunities inside the same argument arc.

10. **Slide 1 title is cover copy** - Keep it short and title-like. Do not use
   the full topic sentence as the cover H1; `html-contract.md` owns the
   detailed cover copy rules.

11. **Cover relay stays simple** - For company, product, AI, infrastructure,
   SaaS, and developer-tool decks, do not plan a labeled process flow,
   architecture map, or explanatory node/card diagram on Slide 1. Slide 1 may
   hand off the title/wordmark when it is the main cover text, or one short key
   phrase into Slide 2; the working system map should begin on Slide 2 or
   later.

12. **Each slide must advance the argument** - Not just list information. If a slide only says "this also exists", merge it or sharpen it.

The outline must be an argument, not a topic inventory. For company, technology, finance, or product decks, avoid a flat encyclopedia sequence such as history, products, market, partnerships, future. Each slide should either advance the thesis, provide evidence, create contrast, answer a risk/question, or resolve the story.

Magic Move should influence slide order and content grouping. Prefer sequences
like index -> focused detail, small metric -> hero metric, system map -> zoomed
node, or comparison row -> evidence slide. Do not add fake repeated labels just
to animate; instead, arrange the argument so real repeated entities can move.
Do not append token rows or "next topic" chips to body slides as the continuity
system; if the label would be ambiguous without the animation, it should not be
there.
For product/AI/infrastructure covers, start complex system-map continuity on
Slide 2 instead of making Slide 1 carry readable diagram nodes.

### Content relay example

```markdown
## Slide 3: Cost becomes the constraint
- Content role: Prove that usage growth creates a margin problem, not just a scale story.
- Content point 1: Adoption is rising faster than unit economics improve.
- Content point 2: The next strategic question is cost per inference.
- Inherited from previous: "Usage Growth" moves from trend-card label into the setup evidence band.
- Passed to next: "Inference Cost" becomes the next slide's main decision variable.
- Content relay / Magic Move plan: Primary anchor: "Inference Cost" moves from small risk card to hero metric panel on Slide 4; Supporting anchors: "$0.03/request"

## Magic Move Storyboard
- Slide 3 -> Slide 4:
  - Content relationship: amplification
  - Primary anchor: "Inference Cost" moves from secondary risk card to full-slide hero metric panel.
  - Supporting anchors: "$0.03/request" grows from card value to pricing-model node.
```

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

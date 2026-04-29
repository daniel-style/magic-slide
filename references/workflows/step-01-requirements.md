## Step 1: Gather Requirements

**CRITICAL: REQUIREMENTS INTAKE IS A HARD GATE**

Before any non-preview deck work, the agent must have explicit user-confirmed
answers for all four question groups below. If any answer is missing, inferred,
or only implied, ask the requirements question and stop. Do not run commands,
search, create folders, write `outline.md`, or draft Brief Lite until this gate
is complete.

1. Topic + audience/lens (what is the deck about, who is it for, and what angle should it take?)
2. Aesthetic style (visual direction)
3. **Language (REQUIRED - never skip, never infer from user's message language)**
4. Images (yes/no for AI-generated images)

**Always ask ALL 4 question groups and wait for user confirmation. Never skip questions or assume defaults without asking.**

**Do NOT infer language from user's message language.** Even if the user writes in Chinese, still ask which language they want for the presentation. The user's interface language and presentation language may be different.

**Do NOT infer the topic lens from a URL, company/product name, or "介绍一下 X".**
Those inputs identify a subject, not the audience, purpose, or narrative angle.
Ask the user to confirm the lens before outlining.

If the user already supplied one or more answers explicitly, restate those
answers in the intake question and let the user confirm or revise them. Values
chosen by the agent are not explicit answers.

### MUST Use AskUserQuestion Tool

**CRITICAL:** You MUST use the AskUserQuestion tool for requirements gathering. Text-based interaction is ONLY a fallback if the tool is unavailable.

**Try AskUserQuestion first:**

```python
AskUserQuestion(
    questions=[
        {
            "question": "What's the presentation about, who is it for, and what angle should it take?",
            "header": "Topic & Lens",
            "options": [],  # Free text input
            "multiSelect": False
        },
        {
            "question": "What aesthetic style would you like?",
            "header": "Style",
            "options": [
                {
                    "label": "Auto (I'll choose based on topic)",
                    "description": "Recommended. I'll analyze your topic and choose the best aesthetic direction."
                },
                {
                    "label": "Minimal & Refined",
                    "description": "Clean layouts, generous whitespace, subtle colors, refined typography."
                },
                {
                    "label": "Bold & Dramatic",
                    "description": "Dark themes, electric accents, geometric layouts, strong contrasts."
                },
                {
                    "label": "Playful & Creative",
                    "description": "Bright colors, asymmetric layouts, energetic fonts, bouncy animations."
                },
                {
                    "label": "Luxury & Elegant",
                    "description": "Black/gold palette, refined serif fonts, sophisticated spacing."
                },
                {
                    "label": "Brutalist & Raw",
                    "description": "Stark contrasts, grid-based, minimal decoration, bold typography."
                },
                {
                    "label": "Organic & Natural",
                    "description": "Earth tones, serif fonts, flowing layouts, soft shadows."
                }
            ],
            "multiSelect": False
        },
        {
            "question": "Which language?",
            "header": "Language",
            "options": [
                {
                    "label": "English",
                    "description": "English language presentation"
                },
                {
                    "label": "中文",
                    "description": "Chinese language presentation"
                },
                {
                    "label": "日本語",
                    "description": "Japanese language presentation"
                },
                {
                    "label": "Español",
                    "description": "Spanish language presentation"
                },
                {
                    "label": "Français",
                    "description": "French language presentation"
                }
            ],
            "multiSelect": False
        },
        {
            "question": "Include AI-generated images?",
            "header": "Images",
            "options": [
                {
                    "label": "No",
                    "description": "Text-only presentation (faster, recommended)"
                },
                {
                    "label": "Yes",
                    "description": "Generate images for key slides (slower, requires image prompts)"
                }
            ],
            "multiSelect": False
        }
    ]
)

# Extract answers
topic = answers["What's the presentation about, who is it for, and what angle should it take?"]
aesthetic_style = answers["What aesthetic style would you like?"]
language = answers["Which language?"]
include_images = answers["Include AI-generated images?"] == "Yes"
```

### Fallback: Text-based (Only if AskUserQuestion fails)

**ONLY use this if AskUserQuestion tool is not available or fails.**

Ask all 4 question groups in plain text as the whole response for the turn,
waiting for each answer before proceeding. Do not assume defaults without
explicit user confirmation.

Follow [text-question-templates.md](text-question-templates.md). End the
plain-text question with a copyable template; localize the lead-in and field
labels to the user's conversation language. English example:

```text
You can copy this template and fill it in:

Topic + audience/lens:
Style: [Auto / Minimal & Refined / Bold & Dramatic / Playful & Creative / Luxury & Elegant / Brutalist & Raw / Organic & Natural / custom]
Language: [English / Chinese / Japanese / Spanish / French / other]
Images: [No / Yes]
```

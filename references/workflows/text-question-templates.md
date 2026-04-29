## Text Question Templates

Use this only when AskUserQuestion is unavailable or fails and the workflow must
fall back to plain-text questions.

When asking structured questions in plain text:

- Ask the questions clearly first.
- End with a short localized line such as "You can copy this template and fill
  it in:" or, in Chinese, "您可以复制以下模板进行填写：".
- Provide a fenced `text` block with one field per question.
- Leave free-text fields blank and put choice fields in brackets.
- Match the field labels to the user's conversation language.
- Keep the template short enough to copy without editing unrelated prose.
- Do not pre-fill defaults unless the user already gave that information.
- Wait for an explicit answer or confirmation before proceeding.

Prefer descriptive field labels over number-only replies, because labels survive
partial answers and make follow-up corrections easier.

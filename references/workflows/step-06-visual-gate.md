## Optional: Pass Visual Gate

Use this gate only with the optional prototype workflow. The default fast path
skips prototype gating and relies on final QA after generating the production
deck.

### Review Rendered Prototype

Open the prototype preview and check:
- HTML and console errors
- Overflow or clipped text
- Sparse slides pushed too high
- Headings/cards/diagrams/source notes overlapping
- Inline SVG black fills or broken connectors
- Image loading, if images were requested
- Magic Move behavior on the sampled transitions

### Decide

If the prototype is acceptable, proceed to the production source pass.

If it fails, revise only the affected CSS/slides, re-merge, re-inject, and
preview again. Avoid using this optional loop when the user has asked for speed
or lower token usage.

## Step 2: Web Search (Ask User First)

**CRITICAL:** Do NOT search automatically. Always ask the user first.

### MUST Use AskUserQuestion Tool

**CRITICAL:** You MUST use the AskUserQuestion tool to ask about web search. Text-based interaction is ONLY a fallback if the tool is unavailable.

**Try AskUserQuestion first:**

```python
AskUserQuestion(
    questions=[
        {
            "question": f"Do you want me to search online for information about '{topic}'?",
            "header": "Web Search",
            "options": [
                {
                    "label": "No",
                    "description": "Skip search, generate from my knowledge (faster)"
                },
                {
                    "label": "Yes",
                    "description": "Search for current info, examples, and context"
                }
            ],
            "multiSelect": False
        }
    ]
)

if answers[...] == "Yes":
    # Find skill directory first
    import subprocess
    skill_dir_result = subprocess.run(
        'find ~ -type d -name "magic-slide-skill" 2>/dev/null | head -1',
        shell=True, capture_output=True, text=True
    )
    SKILL_DIR = skill_dir_result.stdout.strip()
    
    # Generate multiple search queries for comprehensive coverage
    search_queries = [
        f"{topic} overview key points",
        f"{topic} latest developments 2026",
        f"{topic} examples case studies",
        f"{topic} statistics data trends"
    ]
    
    # Execute searches in parallel using multiple Bash calls
    search_results = []
    for query in search_queries:
        result = Bash(
            command=f'python3 "{SKILL_DIR}/scripts/websearch.py" "{query}"',
            description=f"Search: {query}"
        )
        if result.exit_code == 0:
            try:
                import json
                data = json.loads(result.stdout)
                search_results.extend(data.get("organic", [])[:3])  # Top 3 from each query
            except:
                pass
    
    # Deduplicate by URL and format context
    seen_urls = set()
    unique_results = []
    for r in search_results:
        url = r.get("link", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)
    
    if not unique_results:
        # Search was requested but produced no usable results. Try another
        # available search tool. If none exists, tell the user search failed and
        # ask whether to proceed without current sources.
        raise RuntimeError("Web search requested but no usable results were collected")

    # Format search context for outline generation
    search_context = "\n\n".join([
        f"**{r['title']}**\n{r['snippet']}\nSource: {r['link']}"
        for r in unique_results[:10]  # Top 10 unique results
    ])
    # Incorporate search_context into outline generation in Step 3
```

### Fallback: Text-based (Only if AskUserQuestion fails)

**ONLY use this if AskUserQuestion tool is not available or fails.**

Ask the user in plain text whether they want web search for their topic. If yes, find the skill directory and use `$SKILL_DIR/scripts/websearch.py` via Bash for each query in parallel, then incorporate combined results into the outline.

If web search was requested and every query fails, pause before outlining. Either use another available search capability or ask the user to approve proceeding without current sources. For modern companies, products, laws, prices, statistics, or news, do not replace failed search with unsourced memory without explicit user approval.


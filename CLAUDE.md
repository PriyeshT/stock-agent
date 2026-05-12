# CLAUDE.md — Stock Agent Project Constitution

> This file tells Claude Code exactly how to behave in this project.
> Read this fully before doing anything. Reference it when making decisions.

---

## What This Project Is

An agentic AI system that researches 9 pre-selected stocks across AI, Defence,
and Medical domains. Produces a weekly brief in Notion every Monday 7AM SGT.
Built by a business consultant as a learning experiment — not a developer.

Full context in: `docs/project-brief.md`

---

## Who Is Building This

Priyesh — Associate Director, AI delivery lead, business consultant.
Not a developer. Comfortable with logic, systems thinking, and product design.
Learning LangChain and agentic AI patterns to advise clients credibly.

**Implications for how Claude Code should behave:**
- Always explain *why* before *how*
- When writing code, add a plain English comment above every function
- When making architectural decisions, explain the tradeoff in business terms
- Never assume prior Python or LangChain knowledge — always explain new patterns
- If something can be done two ways, explain both briefly and recommend one

---

## The Stack

```
Language:        Python 3.11+
Agent framework: LangChain
LLM:             Claude API — model: claude-sonnet-4-20250514
Web search:      Tavily API
Data store:      Notion API
Scheduling:      GitHub Actions
Observability:   LangSmith
Testing:         pytest
Env management:  python-dotenv (.env file)
```

---

## Project Structure

```
stock-agent/
│
├── CLAUDE.md                          # This file
├── README.md                          # Setup and run instructions
├── requirements.txt                   # All dependencies
├── .env.example                       # API key template (never commit .env)
│
├── .github/
│   └── workflows/
│       └── weekly-brief.yml           # Monday 11PM UTC trigger
│
├── docs/
│   ├── project-brief.md               # Full system design
│   ├── learning-notes/
│   │   ├── stage-1-chains.md
│   │   ├── stage-2-tools.md
│   │   ├── stage-3-agents.md
│   │   ├── stage-4-memory.md
│   │   ├── stage-5-multiagent.md
│   │   └── stage-6-observability.md
│   └── linkedin-drafts/
│       └── post-draft.md
│
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py          # Researches all 9 watchlist stocks
│   │   ├── portfolio_agent.py         # Monitors holdings, checks sell rules
│   │   └── brief_writer.py            # Formats and posts to Notion
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py              # Tavily search wrapper
│   │   └── notion_client.py           # Notion read/write operations
│   ├── chains/
│   │   ├── __init__.py
│   │   └── stock_research_chain.py    # Stage 1 starting point
│   └── config/
│       ├── __init__.py
│       ├── watchlist.py               # The 9 stocks — do not modify without confirmation
│       └── rules.py                   # Buy/sell rules — do not modify without confirmation
│
├── tests/
│   ├── __init__.py
│   ├── test_research_agent.py
│   ├── test_portfolio_agent.py
│   ├── test_sell_rules.py
│   └── test_brief_writer.py
│
└── notebooks/
    └── stage1_experiments.ipynb       # Safe sandbox for trying things
```

---

## The Watchlist — Do Not Modify Without Confirmation

```python
WATCHLIST = {
    "AI": ["MSFT", "NVDA", "GOOGL"],
    "Defence": ["LMT", "RTX", "LHX"],
    "Medical": ["LLY", "UNH", "ISRG"]
}
```

---

## The Buy/Sell Rules — Do Not Modify Without Confirmation

```python
BUY_RULES = {
    "signal_required": "GREEN",
    "max_positions": 3,
    "buy_frequency": "last_monday_of_month",
    "no_buy_within_days_of_event": 7,
    "no_averaging_down": True
}

SELL_RULES = {
    "partial_exit_at_gain_pct": 25,      # Sell half at +25%
    "full_exit_at_gain_pct": 50,         # Sell all at +50%
    "hard_stop_loss_pct": -15,           # Sell all at -15%
    "story_change": True,                # Sell if thesis breaks
    "yellow_weeks_before_exit": 3        # Exit after 3 consecutive Yellow weeks
}

POSITION_STATES = ["ACTIVE", "PARTIAL", "CLOSED"]
```

---

## Portfolio Table Schema (Notion)

```
Stock            | text
Ticker           | text
Buy Date         | date
Buy Price (USD)  | number
Quantity         | number
Status           | select: ACTIVE / PARTIAL / CLOSED
Partial Sell Price | number (optional)
Full Sell Price  | number (optional)
Notes            | text (optional)
```

---

## Coding Conventions

**Every function must have:**
1. A plain English docstring — what it does, not how
2. Type hints on parameters and return values
3. A corresponding test in the tests/ folder

**Example of correct style:**
```python
def calculate_gain_pct(buy_price: float, current_price: float) -> float:
    """
    Calculate the percentage gain or loss on a position.
    Returns a positive number for gains, negative for losses.
    Example: buy at $100, current $125 → returns 25.0
    """
    return ((current_price - buy_price) / buy_price) * 100
```

**Never:**
- Hardcode API keys anywhere in code
- Modify watchlist.py or rules.py without explicit confirmation
- Skip writing a test for new logic
- Add a new dependency without updating requirements.txt
- Write a function longer than 30 lines — break it up

---

## Learning Notes Convention

After completing each stage, update the corresponding file in
`docs/learning-notes/` using this exact structure:

```markdown
# Stage N — [Name]

## What I Was Trying to Do

## What I Built

## What Surprised Me

## What Broke and How I Fixed It

## What This Means for Enterprise AI

## One Thing I'd Tell a Client About This
```

These notes feed directly into the LinkedIn post. Do not skip them.

---

## Current Stage

**Stage 1 — Building the basic research chain**

Goal: A LangChain chain that takes one stock ticker as input,
runs a Tavily web search, and returns a plain English research summary.
No agent loop yet. Just: input → search → LLM → output.

Start in: `src/chains/stock_research_chain.py`
Experiment in: `notebooks/stage1_experiments.ipynb`

---

## The 6-Stage Learning Plan

| Stage | File(s) to build | Core concept |
|---|---|---|
| 1 | chains/stock_research_chain.py | Chains, prompts, Claude API |
| 2 | tools/web_search.py | Tool use and tool definition |
| 3 | agents/research_agent.py | ReAct agent loop |
| 4 | tools/notion_client.py + agents/portfolio_agent.py | Memory and state |
| 5 | agents/brief_writer.py + orchestration | Multi-agent design |
| 6 | .github/workflows/weekly-brief.yml | Scheduling + observability |

---

## Environment Variables Required

```bash
# .env file — never commit this
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
NOTION_API_KEY=your_key_here
NOTION_DATABASE_ID=your_portfolio_table_id
NOTION_PARENT_PAGE_ID=your_stock_agent_root_page_id
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=stock-agent
```

---

## CI/CD — GitHub Actions

**On every push to main:**
- Run pytest across all tests
- Block merge if any test fails

**Every Sunday 11PM UTC (Monday 7AM SGT):**
- Run the full agent pipeline
- Post brief to Notion
- Log run to LangSmith
- Email on failure

**Workflow file:** `.github/workflows/weekly-brief.yml`

---

## What Success Looks Like

**Stage 1 done when:**
A single function call with ticker "NVDA" returns a readable 3–4 sentence
research summary based on real web search results.

**Full MVP done when:**
Every Monday morning, a new brief appears in Notion without any manual
intervention, and the portfolio watch section correctly flags any
triggered sell rules.

**Learning done when:**
All 6 learning notes are written and the LinkedIn post draft exists
in `docs/linkedin-drafts/post-draft.md`.

---

## Do Not Do These Things

- Do not build a UI — this runs headless
- Do not connect to any broker API — execution is always manual
- Do not store financial data beyond what's in the Notion table
- Do not run the agent more than once per week in production
- Do not over-engineer Stage 1 — a working chain beats a perfect architecture

# Stock Agent

An agentic AI system that researches 9 pre-selected stocks and posts a
structured weekly brief to Notion every Monday at 7AM SGT.

Built with LangChain, Claude, Tavily, and Notion. Scheduled via GitHub Actions.

---

## Quickstart

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd stock-agent
```

### 2. Create a Python virtual environment

A virtual environment keeps this project's dependencies separate from anything
else on your machine. Think of it as a clean room for this project only.

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Open .env and fill in your real API keys
```

You'll need accounts and API keys for:
- [Anthropic](https://console.anthropic.com) — for Claude
- [Tavily](https://tavily.com) — for web search
- [Notion](https://www.notion.so/my-integrations) — for reading/writing briefs
- [LangSmith](https://smith.langchain.com) — for observability (free tier fine)

### 5. Run the tests

```bash
pytest
```

All tests should pass. If they don't, check your Python version (`python3 --version` should be 3.11+).

---

## Project Structure

```
src/
  chains/         Stage 1 — basic research chain (start here)
  tools/          Stage 2 — Tavily search + Notion client
  agents/         Stage 3–5 — research, portfolio, and brief writer agents
  config/         Watchlist and buy/sell rules (do not modify without confirmation)

tests/            One test file per source file
docs/
  learning-notes/ Fill in after each stage — feeds the LinkedIn post
  project-brief.md Full system design

notebooks/        Safe sandbox for Stage 1 experiments
.github/workflows/ GitHub Actions — tests on push, agent run on schedule
```

---

## The 9 Stocks

| Sector   | Tickers           |
|----------|-------------------|
| AI       | MSFT, NVDA, GOOGL |
| Defence  | LMT, RTX, LHX     |
| Medical  | LLY, UNH, ISRG    |

---

## Current Stage

**Stage 1** — Building the basic research chain.

See `src/chains/stock_research_chain.py` and experiment in
`notebooks/stage1_experiments.ipynb`.

---

## Running the Agent Manually

Once all stages are complete:

```bash
# TODO (Stage 6): add entry point command here
```

The agent also runs automatically every Sunday at 11PM UTC (Monday 7AM SGT)
via GitHub Actions.

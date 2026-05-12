# Stock Agent — Project Brief

## What This Is

An agentic AI system that monitors 9 pre-selected stocks across three sectors
(AI, Defence, Medical) and produces a structured weekly brief in Notion
every Monday morning at 7AM SGT — without any manual intervention.

## Why I'm Building This

1. **Learning**: To understand LangChain and agentic AI patterns well enough
   to advise enterprise clients credibly — not just theoretically.
2. **Personal use**: To have a systematic, repeatable research process for
   my own investment watchlist.

## The 9 Stocks

| Sector   | Tickers              |
|----------|----------------------|
| AI       | MSFT, NVDA, GOOGL    |
| Defence  | LMT, RTX, LHX        |
| Medical  | LLY, UNH, ISRG       |

## What the System Does Each Week

1. Searches the web for recent news on each of the 9 stocks (Tavily)
2. Asks Claude to rate each stock: GREEN / YELLOW / RED
3. Checks the Notion portfolio table against buy/sell rules
4. Flags any positions that have hit a trigger (stop loss, profit target, etc.)
5. Writes a structured brief to Notion with all findings
6. Logs the entire run to LangSmith for debugging

## What It Does NOT Do

- Execute trades (manual only)
- Connect to any broker API
- Store financial data outside Notion
- Run more than once per week

## The 6-Stage Learning Plan

| Stage | What I'm Building | What I'm Learning |
|-------|-------------------|-------------------|
| 1 | Basic research chain | Chains, prompts, Claude API |
| 2 | Web search tool | Tool definition and wrapping |
| 3 | Research agent | ReAct agent loop |
| 4 | Portfolio agent + Notion | Memory, state, external APIs |
| 5 | Brief writer + orchestration | Multi-agent coordination |
| 6 | Scheduling + observability | GitHub Actions, LangSmith |

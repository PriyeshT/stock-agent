# DO NOT MODIFY without explicit confirmation from Priyesh.
# This is the single source of truth for which stocks the agent monitors.

WATCHLIST: dict[str, list[str]] = {
    "AI": ["MSFT", "NVDA", "GOOGL"],
    "Defence": ["LMT", "RTX", "LHX"],
    "Medical": ["LLY", "UNH", "ISRG"],
}

# Flat list of all tickers — useful when you need to loop over every stock
ALL_TICKERS: list[str] = [
    ticker
    for tickers in WATCHLIST.values()
    for ticker in tickers
]

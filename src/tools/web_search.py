import os
from perplexity import Perplexity
from langchain_core.tools import tool


@tool
def search_stock_news(ticker: str) -> str:
    """
    Search for recent news, earnings results, and analyst sentiment for a stock ticker.
    Use this tool when you need up-to-date information about a specific stock before
    writing a research summary. Input must be a stock ticker symbol such as NVDA or MSFT.
    Returns a structured summary of recent sources with titles, URLs, dates, and snippets.
    """
    if not os.getenv("PERPLEXITY_API_KEY"):
        raise ValueError("PERPLEXITY_API_KEY is not set in your .env file")

    client = Perplexity()
    search = client.search.create(
        query=f"{ticker} stock latest news earnings analyst sentiment",
        max_results=5,
        max_tokens_per_page=4096,
    )

    lines = []
    for result in search.results:
        lines.append(
            f"Title: {result.title}\n"
            f"URL: {result.url}\n"
            f"Date: {result.date}\n"
            f"{result.snippet}"
        )

    return "\n\n---\n\n".join(lines)

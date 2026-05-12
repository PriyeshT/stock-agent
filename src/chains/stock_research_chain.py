import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

# The Claude model to use. Must match a real Anthropic API model ID.
MODEL = "claude-sonnet-4-6-20250514"

# How many search results to fetch per ticker — more results = better coverage, slower run
MAX_SEARCH_RESULTS = 5


def search_stock_news(ticker: str) -> str:
    """
    Search the web for recent news about a stock ticker.
    Returns all results joined into one string, ready to drop into a prompt.
    Example input: "NVDA" → returns several paragraphs of recent news text.
    """
    tool = TavilySearchResults(max_results=MAX_SEARCH_RESULTS)
    results = tool.invoke(f"{ticker} stock news analysis latest")

    lines = []
    for r in results:
        lines.append(f"URL: {r['url']}\n{r['content']}")

    return "\n\n---\n\n".join(lines)


def build_summary_prompt() -> ChatPromptTemplate:
    """
    Define the prompt template we send to Claude.
    The {ticker} and {news} placeholders are filled in at runtime when the chain runs.
    The system message sets Claude's persona; the human message provides the actual data.
    """
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a concise stock analyst writing for a retail investor. "
            "Summarise the current situation in 3-4 plain English sentences. "
            "End with one sentence on overall outlook: bullish, neutral, or bearish.",
        ),
        (
            "human",
            "Ticker: {ticker}\n\nRecent news:\n{news}\n\nWrite your summary now.",
        ),
    ])


def build_research_chain():
    """
    Assemble the three-step chain: prompt → Claude LLM → plain text parser.
    The | operator is LangChain's way of connecting steps — output of one feeds into the next.
    Returns a runnable chain object. Call .invoke({"ticker": ..., "news": ...}) to run it.
    """
    llm = ChatAnthropic(model=MODEL)
    prompt = build_summary_prompt()
    parser = StrOutputParser()  # strips the LLM response object down to a plain string
    return prompt | llm | parser


def research_stock(ticker: str) -> str:
    """
    Research a single stock ticker and return a plain English summary.
    This is the main entry point for Stage 1 — call this function with any watchlist ticker.
    Example: research_stock("NVDA") → "NVIDIA reported strong earnings..."
    """
    news = search_stock_news(ticker)
    chain = build_research_chain()
    return chain.invoke({"ticker": ticker, "news": news})

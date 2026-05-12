import os
from dotenv import load_dotenv
from perplexity import Perplexity
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# The Claude model to use for the final summary step.
MODEL = "claude-sonnet-4-6"

# Disable LangSmith tracing if no API key is configured.
# Prevents noisy connection errors during local development.
if not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "false"


def search_stock_news(ticker: str) -> str:
    """
    Search for recent news about a stock ticker using the Perplexity Search API.
    Returns structured results (title, URL, date, snippet) joined into one string
    ready to pass to Claude as context.
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

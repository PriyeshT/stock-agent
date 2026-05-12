import os
import requests
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# The Claude model to use. Must match a real Anthropic API model ID.
MODEL = "claude-sonnet-4-6"

# Perplexity's "sonar" model searches the web and synthesises results in one call.
# "sonar-pro" is more thorough but slower — fine to swap in later.
PERPLEXITY_MODEL = "sonar"
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Disable LangSmith tracing if no API key is configured.
# Prevents noisy connection errors during local development.
if not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "false"


def search_stock_news(ticker: str) -> str:
    """
    Fetch recent news and analyst sentiment for a stock ticker using Perplexity.
    Unlike a raw search API, Perplexity reads its sources and returns synthesised prose.
    Returns the synthesised text plus source URLs, ready to pass to Claude.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY is not set in your .env file")

    response = requests.post(
        PERPLEXITY_API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": PERPLEXITY_MODEL,
            "messages": [{
                "role": "user",
                "content": (
                    f"What is the latest news and analyst sentiment for {ticker} stock? "
                    "Focus on recent earnings, price movements, and key developments."
                ),
            }],
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])

    if citations:
        sources = "\n".join(f"- {url}" for url in citations)
        return f"{content}\n\nSources:\n{sources}"

    return content


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

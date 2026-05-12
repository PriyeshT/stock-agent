import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.web_search import search_stock_news

load_dotenv()

# The Claude model to use for the final summary step.
MODEL = "claude-sonnet-4-6"

# Disable LangSmith tracing if no API key is configured.
# Prevents noisy connection errors during local development.
if not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "false"


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
    parser = StrOutputParser()
    return prompt | llm | parser


def research_stock(ticker: str) -> str:
    """
    Research a single stock ticker and return a plain English summary.
    This is the main entry point — call this function with any watchlist ticker.
    Example: research_stock("NVDA") → "NVIDIA reported strong earnings..."
    """
    # .invoke() is how you call a LangChain Tool — same method as calling a chain
    news = search_stock_news.invoke(ticker)
    chain = build_research_chain()
    return chain.invoke({"ticker": ticker, "news": news})

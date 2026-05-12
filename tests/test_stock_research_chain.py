# Tests for src/chains/stock_research_chain.py
# Covers chain assembly and orchestration only.
# Tool behaviour is tested separately in test_web_search_tool.py.

from unittest.mock import MagicMock, patch

from src.chains.stock_research_chain import (
    build_research_chain,
    build_summary_prompt,
    research_stock,
)


def test_build_summary_prompt_has_required_variables() -> None:
    """
    Confirm the prompt template has both slots we need to fill at runtime.
    If either is missing, the chain will crash when it runs.
    """
    prompt = build_summary_prompt()
    assert "ticker" in prompt.input_variables
    assert "news" in prompt.input_variables


def test_research_stock_calls_tool_invoke() -> None:
    """
    Confirm research_stock calls search_stock_news.invoke() — not the function directly.
    Tools must be called via .invoke() so LangChain can apply tracing and middleware.
    """
    fake_summary = "NVIDIA is performing well. Outlook: bullish."

    with patch("src.chains.stock_research_chain.search_stock_news") as mock_tool:
        mock_tool.invoke.return_value = "some news"
        with patch("src.chains.stock_research_chain.build_research_chain") as mock_builder:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = fake_summary
            mock_builder.return_value = mock_chain

            result = research_stock("NVDA")

    mock_tool.invoke.assert_called_once_with("NVDA")
    assert result == fake_summary


def test_research_stock_passes_news_and_ticker_to_chain() -> None:
    """
    Confirm both the ticker and the news from the tool are passed to the chain.
    If either is missing, Claude won't have enough context to write a summary.
    """
    fake_news = "NVDA revenue up 20%."
    fake_summary = "NVIDIA beats expectations. Outlook: bullish."

    with patch("src.chains.stock_research_chain.search_stock_news") as mock_tool:
        mock_tool.invoke.return_value = fake_news
        with patch("src.chains.stock_research_chain.build_research_chain") as mock_builder:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = fake_summary
            mock_builder.return_value = mock_chain

            research_stock("NVDA")

    mock_chain.invoke.assert_called_once_with({"ticker": "NVDA", "news": fake_news})


def test_research_stock_passes_correct_ticker() -> None:
    """
    Confirm the ticker flows through correctly — not hardcoded anywhere.
    """
    with patch("src.chains.stock_research_chain.search_stock_news") as mock_tool:
        mock_tool.invoke.return_value = "news"
        with patch("src.chains.stock_research_chain.build_research_chain") as mock_builder:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "summary"
            mock_builder.return_value = mock_chain

            research_stock("LMT")

    call_args = mock_chain.invoke.call_args[0][0]
    assert call_args["ticker"] == "LMT"

# Tests for src/chains/stock_research_chain.py
# All external API calls (Tavily, Claude) are mocked — no real network requests.
# "Mocking" means we replace the real API call with a fake one that returns
# a value we control, so we can test our logic in isolation.

from unittest.mock import MagicMock, patch

from src.chains.stock_research_chain import (
    build_research_chain,
    build_summary_prompt,
    research_stock,
    search_stock_news,
)


def test_search_stock_news_formats_results() -> None:
    """
    Verify that raw Tavily results are joined into one string with separators.
    We fake the Tavily response so no real search happens.
    """
    fake_results = [
        {"url": "https://example.com/1", "content": "NVDA beats earnings expectations."},
        {"url": "https://example.com/2", "content": "NVDA stock rises 5% after hours."},
    ]
    with patch("src.chains.stock_research_chain.TavilySearchResults") as mock_tavily:
        mock_tavily.return_value.invoke.return_value = fake_results
        result = search_stock_news("NVDA")

    assert "NVDA beats earnings expectations." in result
    assert "NVDA stock rises 5% after hours." in result
    assert "---" in result  # separator between results is present


def test_search_stock_news_includes_urls() -> None:
    """
    Verify that each result's URL is included so the summary can cite sources.
    """
    fake_results = [{"url": "https://reuters.com/nvda", "content": "Some news."}]
    with patch("src.chains.stock_research_chain.TavilySearchResults") as mock_tavily:
        mock_tavily.return_value.invoke.return_value = fake_results
        result = search_stock_news("NVDA")

    assert "https://reuters.com/nvda" in result


def test_build_summary_prompt_has_required_variables() -> None:
    """
    Confirm the prompt template has both slots we need to fill at runtime.
    If either is missing, the chain will crash when it runs.
    """
    prompt = build_summary_prompt()
    assert "ticker" in prompt.input_variables
    assert "news" in prompt.input_variables


def test_research_stock_returns_string() -> None:
    """
    End-to-end test: research_stock calls search, then the chain, returns the summary.
    Both external dependencies are mocked — we're testing that the orchestration is correct.
    """
    fake_news = "NVDA is performing well."
    fake_summary = "NVIDIA continues to lead the AI chip market. Outlook: bullish."

    with patch("src.chains.stock_research_chain.search_stock_news", return_value=fake_news):
        with patch("src.chains.stock_research_chain.build_research_chain") as mock_builder:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = fake_summary
            mock_builder.return_value = mock_chain

            result = research_stock("NVDA")

    assert result == fake_summary
    # Confirm the chain received both the ticker and the news we provided
    mock_chain.invoke.assert_called_once_with({"ticker": "NVDA", "news": fake_news})


def test_research_stock_passes_correct_ticker() -> None:
    """
    Confirm the ticker is passed through correctly — not hardcoded anywhere.
    Regression guard: if someone accidentally hardcodes "NVDA", this catches it.
    """
    with patch("src.chains.stock_research_chain.search_stock_news", return_value="news"):
        with patch("src.chains.stock_research_chain.build_research_chain") as mock_builder:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "summary"
            mock_builder.return_value = mock_chain

            research_stock("MSFT")

    call_args = mock_chain.invoke.call_args[0][0]
    assert call_args["ticker"] == "MSFT"

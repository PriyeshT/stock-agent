# Tests for src/chains/stock_research_chain.py
# All external API calls (Perplexity, Claude) are mocked — no real network requests.

from unittest.mock import MagicMock, patch

from src.chains.stock_research_chain import (
    build_research_chain,
    build_summary_prompt,
    research_stock,
    search_stock_news,
)


def _make_result(title: str, url: str, snippet: str, date: str = "2025-01-01") -> MagicMock:
    """
    Build a fake Perplexity search result object.
    Helper used by multiple tests — not a test itself.
    """
    result = MagicMock()
    result.title = title
    result.url = url
    result.snippet = snippet
    result.date = date
    return result


def _mock_perplexity(results: list) -> MagicMock:
    """
    Build a fake Perplexity client whose search.create returns the given results.
    Patches the Perplexity class so no real SDK call is made.
    """
    mock_client = MagicMock()
    mock_client.search.create.return_value.results = results
    return mock_client


def test_search_stock_news_includes_title_url_and_snippet() -> None:
    """
    Verify that each result's title, URL, and snippet all appear in the output.
    Claude needs all three to write a grounded summary.
    """
    fake_results = [
        _make_result("NVDA Beats Earnings", "https://reuters.com/nvda", "Revenue up 20%.", "2025-05-01"),
    ]
    with patch("src.chains.stock_research_chain.Perplexity", return_value=_mock_perplexity(fake_results)):
        result = search_stock_news("NVDA")

    assert "NVDA Beats Earnings" in result
    assert "https://reuters.com/nvda" in result
    assert "Revenue up 20%." in result
    assert "2025-05-01" in result


def test_search_stock_news_joins_multiple_results() -> None:
    """
    Verify that multiple results are separated — not just the first one returned.
    """
    fake_results = [
        _make_result("Story 1", "https://a.com", "Content A."),
        _make_result("Story 2", "https://b.com", "Content B."),
    ]
    with patch("src.chains.stock_research_chain.Perplexity", return_value=_mock_perplexity(fake_results)):
        result = search_stock_news("MSFT")

    assert "Content A." in result
    assert "Content B." in result
    assert "---" in result  # separator between results


def test_search_stock_news_raises_without_api_key() -> None:
    """
    Confirm we get a clear error message if PERPLEXITY_API_KEY is missing.
    Better to fail loudly with a helpful message than crash inside the SDK.
    """
    import os
    original = os.environ.pop("PERPLEXITY_API_KEY", None)
    try:
        try:
            search_stock_news("NVDA")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "PERPLEXITY_API_KEY" in str(e)
    finally:
        if original:
            os.environ["PERPLEXITY_API_KEY"] = original


def test_build_summary_prompt_has_required_variables() -> None:
    """
    Confirm the prompt template has both slots we need to fill at runtime.
    If either is missing, the chain will crash when it runs.
    """
    prompt = build_summary_prompt()
    assert "ticker" in prompt.input_variables
    assert "news" in prompt.input_variables


def test_research_stock_returns_summary() -> None:
    """
    End-to-end test: research_stock calls search, then the chain, returns the summary.
    Both external dependencies are mocked.
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
    mock_chain.invoke.assert_called_once_with({"ticker": "NVDA", "news": fake_news})


def test_research_stock_passes_correct_ticker() -> None:
    """
    Confirm the ticker is passed through correctly — not hardcoded anywhere.
    """
    with patch("src.chains.stock_research_chain.search_stock_news", return_value="news"):
        with patch("src.chains.stock_research_chain.build_research_chain") as mock_builder:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "summary"
            mock_builder.return_value = mock_chain

            research_stock("LMT")

    call_args = mock_chain.invoke.call_args[0][0]
    assert call_args["ticker"] == "LMT"

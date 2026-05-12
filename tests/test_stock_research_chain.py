# Tests for src/chains/stock_research_chain.py
# All external API calls (Perplexity, Claude) are mocked — no real network requests.

from unittest.mock import MagicMock, patch

from src.chains.stock_research_chain import (
    build_research_chain,
    build_summary_prompt,
    research_stock,
    search_stock_news,
)


def _mock_perplexity_response(content: str, citations: list[str] | None = None) -> MagicMock:
    """
    Build a fake requests.Response object that looks like a Perplexity API reply.
    This is a helper used by multiple tests below — not a test itself.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": content}}],
        "citations": citations or [],
    }
    return mock_response


def test_search_stock_news_returns_content() -> None:
    """
    Verify that the synthesised text from Perplexity is returned as-is.
    """
    fake_content = "NVDA beats earnings expectations. Revenue up 20%."

    with patch("src.chains.stock_research_chain.requests.post") as mock_post:
        mock_post.return_value = _mock_perplexity_response(fake_content)
        result = search_stock_news("NVDA")

    assert fake_content in result


def test_search_stock_news_appends_citations() -> None:
    """
    Verify that source URLs are appended when Perplexity returns citations.
    We want sources in the output so Claude's summary is grounded in real references.
    """
    fake_citations = ["https://reuters.com/nvda", "https://bloomberg.com/nvda"]

    with patch("src.chains.stock_research_chain.requests.post") as mock_post:
        mock_post.return_value = _mock_perplexity_response("Some news.", fake_citations)
        result = search_stock_news("NVDA")

    assert "https://reuters.com/nvda" in result
    assert "https://bloomberg.com/nvda" in result


def test_search_stock_news_raises_without_api_key() -> None:
    """
    Confirm we get a clear error message if PERPLEXITY_API_KEY is missing.
    Better to fail loudly with a helpful message than silently return nothing.
    """
    with patch.dict("os.environ", {}, clear=False):
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

            research_stock("MSFT")

    call_args = mock_chain.invoke.call_args[0][0]
    assert call_args["ticker"] == "MSFT"

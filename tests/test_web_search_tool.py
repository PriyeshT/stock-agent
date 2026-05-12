# Tests for src/tools/web_search.py
# Verifies the tool's structure (name, description, schema) and its runtime behaviour.

from unittest.mock import MagicMock, patch

from src.tools.web_search import search_stock_news


def _make_result(title: str, url: str, snippet: str, date: str = "2025-01-01") -> MagicMock:
    result = MagicMock()
    result.title = title
    result.url = url
    result.snippet = snippet
    result.date = date
    return result


def _mock_perplexity(results: list) -> MagicMock:
    mock_client = MagicMock()
    mock_client.search.create.return_value.results = results
    return mock_client


def test_tool_has_correct_name() -> None:
    """
    The tool name is what the agent uses to refer to this tool in its reasoning.
    If it changes accidentally, the agent won't be able to call it.
    """
    assert search_stock_news.name == "search_stock_news"


def test_tool_has_description() -> None:
    """
    The description is what the LLM reads to decide whether to call this tool.
    It must exist and be non-empty — a missing description makes the tool invisible to agents.
    """
    assert search_stock_news.description
    assert len(search_stock_news.description) > 20


def test_tool_description_mentions_ticker() -> None:
    """
    The description should mention 'ticker' so the agent knows what input to provide.
    """
    assert "ticker" in search_stock_news.description.lower()


def test_tool_has_string_input_schema() -> None:
    """
    Confirm the tool expects a single string argument.
    The agent constructs inputs from this schema — wrong schema means wrong calls.
    """
    schema = search_stock_news.args
    assert "ticker" in schema
    assert schema["ticker"]["type"] == "string"


def test_tool_returns_formatted_results() -> None:
    """
    Verify the tool formats each result with title, URL, date, and snippet.
    """
    fake_results = [
        _make_result("NVDA Earnings Beat", "https://reuters.com", "Revenue up 20%.", "2025-05-01"),
    ]
    with patch("src.tools.web_search.Perplexity", return_value=_mock_perplexity(fake_results)):
        result = search_stock_news.invoke("NVDA")

    assert "NVDA Earnings Beat" in result
    assert "https://reuters.com" in result
    assert "Revenue up 20%." in result
    assert "2025-05-01" in result


def test_tool_raises_without_api_key() -> None:
    """
    Confirm the tool raises a clear error if PERPLEXITY_API_KEY is missing.
    """
    import os
    original = os.environ.pop("PERPLEXITY_API_KEY", None)
    try:
        try:
            search_stock_news.invoke("NVDA")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "PERPLEXITY_API_KEY" in str(e)
    finally:
        if original:
            os.environ["PERPLEXITY_API_KEY"] = original

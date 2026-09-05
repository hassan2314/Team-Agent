"""Unit tests for GitHub tools (mocked HTTP — no network/API keys required)."""

from unittest.mock import MagicMock, patch

from my_agent.tools.github_tools import get_readme, get_repo_info, list_top_issues


def _mock_response(status_code=200, json_data=None, text=""):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = json_data or {}
    return response


@patch("my_agent.tools.github_tools.requests.get")
def test_get_repo_info_success(mock_get):
    mock_get.return_value = _mock_response(
        json_data={
            "full_name": "fastapi/fastapi",
            "description": "FastAPI framework",
            "stargazers_count": 1000,
            "forks_count": 100,
            "open_issues_count": 10,
            "language": "Python",
            "license": {"spdx_id": "MIT"},
            "topics": ["api"],
            "html_url": "https://github.com/fastapi/fastapi",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    )

    result = get_repo_info("fastapi", "fastapi")

    assert result["status"] == "success"
    assert result["full_name"] == "fastapi/fastapi"
    assert result["stars"] == 1000
    mock_get.assert_called_once()


@patch("my_agent.tools.github_tools.requests.get")
def test_get_repo_info_not_found(mock_get):
    mock_get.return_value = _mock_response(status_code=404)

    result = get_repo_info("nope", "missing")

    assert result["status"] == "error"
    assert "not found" in result["error_message"].lower()


@patch("my_agent.tools.github_tools.requests.get")
def test_get_readme_success(mock_get):
    mock_get.return_value = _mock_response(text="# FastAPI\n\nGreat framework.")

    result = get_readme("fastapi", "fastapi")

    assert result["status"] == "success"
    assert "FastAPI" in result["readme"]


@patch("my_agent.tools.github_tools.requests.get")
def test_list_top_issues_skips_pull_requests(mock_get):
    mock_get.return_value = _mock_response(
        json_data=[
            {
                "number": 1,
                "title": "Real issue",
                "comments": 3,
                "html_url": "https://github.com/fastapi/fastapi/issues/1",
                "labels": [{"name": "bug"}],
            },
            {
                "number": 2,
                "title": "A PR",
                "comments": 1,
                "html_url": "https://github.com/fastapi/fastapi/pull/2",
                "labels": [],
                "pull_request": {"url": "https://api.github.com/..."},
            },
        ]
    )

    result = list_top_issues("fastapi", "fastapi", limit=5)

    assert result["status"] == "success"
    assert result["count"] == 1
    assert result["issues"][0]["title"] == "Real issue"

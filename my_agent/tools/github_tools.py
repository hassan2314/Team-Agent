import os
import requests

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    token = os.getenv("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-research-team",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_repo_info(owner: str, repo: str) -> dict:
    """Fetch public GitHub repository metadata.

    Args:
        owner: GitHub org or user (e.g. "fastapi").
        repo: Repository name (e.g. "fastapi").

    Returns:
        Dict with status and repo fields, or an error_message.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    try:
        resp = requests.get(url, headers=_headers(), timeout=20)
    except requests.RequestException as e:
        return {"status": "error", "error_message": str(e)}

    if resp.status_code == 404:
        return {"status": "error", "error_message": f"Repo {owner}/{repo} not found."}
    if resp.status_code != 200:
        return {
            "status": "error",
            "error_message": f"GitHub API {resp.status_code}: {resp.text[:200]}",
        }

    data = resp.json()
    return {
        "status": "success",
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "language": data.get("language"),
        "license": (data.get("license") or {}).get("spdx_id"),
        "topics": data.get("topics", []),
        "html_url": data.get("html_url"),
        "updated_at": data.get("updated_at"),
    }


def get_readme(owner: str, repo: str) -> dict:
    """Fetch the README content of a public GitHub repository.

    Args:
        owner: GitHub org or user (e.g. "fastapi").
        repo: Repository name (e.g. "fastapi").

    Returns:
        Dict with status and readme text, or an error_message.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
    headers = {**_headers(), "Accept": "application/vnd.github.raw+json"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException as e:
        return {"status": "error", "error_message": str(e)}

    if resp.status_code == 404:
        return {"status": "error", "error_message": f"No README found for {owner}/{repo}."}
    if resp.status_code != 200:
        return {
            "status": "error",
            "error_message": f"GitHub API {resp.status_code}: {resp.text[:200]}",
        }

    text = resp.text.strip()
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n...[truncated]..."

    return {"status": "success", "owner": owner, "repo": repo, "readme": text}


def list_top_issues(owner: str, repo: str, limit: int = 5) -> dict:
    """List top open issues for a public GitHub repository.

    Args:
        owner: GitHub org or user (e.g. "fastapi").
        repo: Repository name (e.g. "fastapi").
        limit: Max number of issues to return (default 5).

    Returns:
        Dict with status and a list of issues, or an error_message.
    """
    limit = max(1, min(int(limit), 10))
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": limit, "sort": "comments", "direction": "desc"}
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=20)
    except requests.RequestException as e:
        return {"status": "error", "error_message": str(e)}

    if resp.status_code != 200:
        return {
            "status": "error",
            "error_message": f"GitHub API {resp.status_code}: {resp.text[:200]}",
        }

    issues = []
    for item in resp.json():
        if "pull_request" in item:
            continue  # skip PRs; Issues API includes them
        issues.append({
            "number": item.get("number"),
            "title": item.get("title"),
            "comments": item.get("comments"),
            "html_url": item.get("html_url"),
            "labels": [label.get("name") for label in item.get("labels", [])],
        })

    return {
        "status": "success",
        "owner": owner,
        "repo": repo,
        "count": len(issues),
        "issues": issues,
    }
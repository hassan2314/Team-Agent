# Repo Research Team

A multi-agent system built with [Google ADK](https://google.github.io/adk-docs/) that researches public GitHub repositories using **real GitHub API tools**.

Ask about any public repo (for example `fastapi/fastapi`) and get a structured brief covering popularity, purpose, and open-issue health.

## Why this project

Most demos use mock weather tools. This one shows:

- **Multi-agent collaboration** — a coordinator delegates to specialists
- **Real tools** — live GitHub REST API calls (metadata, README, issues)
- **Practical output** — a human-readable “should you use / contribute?” brief

## Architecture

```text
User
  │
  ▼
research_coordinator          (routes the request, writes final brief)
  ├── repo_scout              → get_repo_info
  ├── code_analyst            → get_readme
  └── issue_analyst           → list_top_issues
```

| Agent | Role | Tool |
|-------|------|------|
| `research_coordinator` | Orchestrates specialists and synthesizes the final brief | — |
| `repo_scout` | Stars, forks, license, language, topics | `get_repo_info` |
| `code_analyst` | What the project is for (from README) | `get_readme` |
| `issue_analyst` | Themes in top open issues | `list_top_issues` |

## Project layout

```text
agent-team/
├── README.md
├── .gitignore
├── requirements.txt
└── my_agent/
    ├── __init__.py
    ├── agent.py              # root_agent + sub-agents
    ├── .env.example
    └── tools/
        ├── __init__.py
        └── github_tools.py   # real GitHub API tools
```

## Prerequisites

- Python 3.12+
- A [Gemini API key](https://aistudio.google.com/apikey) (`GOOGLE_API_KEY` or `GEMINI_API_KEY`)
- A GitHub [classic Personal Access Token](https://github.com/settings/tokens) (`GITHUB_TOKEN`) for higher API rate limits

## Setup

```bash
git clone https://github.com/hassan2314/Team-Agent.git
cd Team-Agent

python -m venv .venv
# bash/zsh:
source .venv/bin/activate
# fish:
# source .venv/bin/activate.fish

pip install -r requirements.txt
# Optional: lint + tests tooling
# pip install -r requirements-dev.txt
```

Create your env file:

```bash
cp my_agent/.env.example my_agent/.env
```

Fill in:

```env
GOOGLE_API_KEY=your_gemini_key
GITHUB_TOKEN=ghp_your_github_token
```

Never commit `my_agent/.env`.

## Run

From the project root:

```bash
adk web --port 8000 --reload_agents
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), select `my_agent`, start a session, and try:

```text
Research fastapi/fastapi
```

Other prompts:

```text
Is django/django healthy to contribute to?
Give me a brief on vercel/next.js
```

## Example output (shape)

A successful run typically returns a brief with:

1. **What it is** — short description from repo metadata + README  
2. **Popularity** — stars, forks, primary language, license  
3. **Purpose / audience** — who the project is for  
4. **Health signals** — themes from top open issues  
5. **Should you use it?** — practical recommendation  

## Tech stack

- [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Gemini (`gemini-3.1-flash-lite`)
- GitHub REST API via `requests`

## What I learned

- Multi-**tool** agents vs multi-**agent** teams (`sub_agents` + delegation)
- Writing LLM-friendly tool docstrings and structured `dict` returns
- Wiring real APIs into ADK agents for portfolio-ready demos

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

CI runs the same lint + tests on Python 3.12 via GitHub Actions.

## License

MIT (or your preferred license)

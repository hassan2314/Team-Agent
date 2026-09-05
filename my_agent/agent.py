from google.adk.agents import Agent
from .tools.github_tools import get_repo_info, get_readme, list_top_issues


code_analyst = Agent(
    name="code_analyst",
    model="gemini-3.1-flash-lite",
    description="Reads README and explains what the project does.",
    instruction="Use get_readme. Explain purpose, setup hints, audience. No fluff.",
    tools=[get_readme],
)

issue_analyst = Agent(
    name="issue_analyst",
    model="gemini-3.1-flash-lite",
    description="Summarizes recent open GitHub issues for health signals.",
    instruction="Use list_top_issues. Summarize themes and risk signals.",
    tools=[list_top_issues],
)

repo_scout = Agent(
    name="repo_scout",
    model="gemini-3.1-flash-lite",
    description="Fetches GitHub repository overview metadata.",
    instruction=(
        "You gather repo overview data. "
        "Parse owner/repo from the user (e.g. fastapi/fastapi). "
        "Call get_repo_info. Summarize clearly. Do nothing else."
    ),
    tools=[get_repo_info],
)

root_agent = Agent(
    name="research_coordinator",
    model="gemini-3.1-flash-lite",
    description="Coordinates GitHub repo research specialists.",
    instruction=(
        "You lead a research team for public GitHub repos. "
        "1) Delegate overview to 'repo_scout'. "
        "2) Delegate README/purpose to 'code_analyst'. "
        "3) Delegate issue health to 'issue_analyst'. "
        "4) After specialists report, write a final brief with: "
        "What it is, popularity, purpose, health, should-you-use-it. "
        "If owner/repo is missing, ask once."
    ),
    sub_agents=[repo_scout, code_analyst, issue_analyst],
)
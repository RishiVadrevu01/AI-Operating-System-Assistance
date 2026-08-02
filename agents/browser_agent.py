import logging
from agents.state import AgentState
from tools.browser import open_url, search_youtube, search_google

logger = logging.getLogger(__name__)

async def browser_agent_node(state: AgentState) -> AgentState:
    """Browser Agent node in LangGraph state machine."""
    tool = state.get("selected_tool")
    args = state.get("tool_args", {})
    result = None

    if tool == "open_url":
        url = args.get("url", "https://google.com")
        result = open_url(url)
    elif tool == "search_youtube":
        query = args.get("query", "Python tutorials")
        result = search_youtube(query)
    elif tool == "search_google":
        query = args.get("query", "FastAPI")
        result = search_google(query)
    else:
        result = {"status": "error", "message": f"Unknown browser tool '{tool}'"}

    state["execution_result"] = result
    return state

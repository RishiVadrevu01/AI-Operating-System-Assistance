import logging
from typing import Dict, Any
from agents.state import AgentState
from tools.system import (
    open_application,
    open_folder,
    get_system_stats,
    take_screenshot,
    list_running_processes,
    shutdown_system
)

logger = logging.getLogger(__name__)

async def system_agent_node(state: AgentState) -> AgentState:
    """System Agent node in LangGraph state machine."""
    tool = state.get("selected_tool")
    args = state.get("tool_args", {})
    result = None

    if tool == "open_application":
        app_name = args.get("app_name", "vscode")
        result = open_application(app_name)
    elif tool == "open_folder":
        path = args.get("folder_path", "Downloads")
        result = open_folder(path)
    elif tool == "get_system_stats":
        result = get_system_stats()
    elif tool == "take_screenshot":
        filename = args.get("filename", "screenshot.png")
        result = take_screenshot(filename)
    elif tool == "list_running_processes":
        top_n = args.get("top_n", 5)
        result = list_running_processes(top_n)
    elif tool == "shutdown_system":
        delay = args.get("delay_seconds", 60)
        result = shutdown_system(delay)
    else:
        result = {"status": "error", "message": f"Unknown system tool '{tool}'"}

    state["execution_result"] = result
    return state

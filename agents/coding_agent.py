import logging
from agents.state import AgentState
from tools.coding import create_file, create_folder, execute_terminal_command

logger = logging.getLogger(__name__)

async def coding_agent_node(state: AgentState) -> AgentState:
    """Coding Agent node in LangGraph state machine."""
    tool = state.get("selected_tool")
    args = state.get("tool_args", {})
    result = None

    if tool == "create_file":
        path = args.get("file_path", "test.py")
        content = args.get("content", "# Auto-generated script")
        result = create_file(path, content)
    elif tool == "create_folder":
        path = args.get("folder_path", "NewProject")
        result = create_folder(path)
    elif tool == "execute_terminal_command":
        cmd = args.get("command", "dir")
        result = execute_terminal_command(cmd)
    else:
        result = {"status": "error", "message": f"Unknown coding tool '{tool}'"}

    state["execution_result"] = result
    return state

from typing import TypedDict, Dict, Any, List, Optional

class AgentState(TypedDict):
    user_prompt: str
    target_agent: str
    selected_tool: str
    tool_args: Dict[str, Any]
    explanation: str
    execution_result: Optional[Dict[str, Any]]
    history: List[Dict[str, Any]]

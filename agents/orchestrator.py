import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.system_agent import system_agent_node
from agents.browser_agent import browser_agent_node
from agents.coding_agent import coding_agent_node
from llm.provider import get_llm_response
from db.mongo import db_manager

logger = logging.getLogger(__name__)

async def intent_router_node(state: AgentState) -> AgentState:
    """Analyze prompt via LLM provider and determine target agent & tools."""
    prompt = state["user_prompt"]
    llm_decision = await get_llm_response(prompt)

    state["target_agent"] = llm_decision.get("agent", "general")
    state["selected_tool"] = llm_decision.get("tool", "none")
    state["tool_args"] = llm_decision.get("args", {})
    state["explanation"] = llm_decision.get("explanation", "Processing your request.")
    return state

def route_decision(state: AgentState) -> str:
    """Routing function for conditional edges in LangGraph."""
    agent = state.get("target_agent", "general")
    if agent == "system":
        return "system_agent"
    elif agent == "browser":
        return "browser_agent"
    elif agent == "coding":
        return "coding_agent"
    return "general_responder"

async def general_responder_node(state: AgentState) -> AgentState:
    """Node for conversational queries or direct explanations."""
    state["execution_result"] = {
        "status": "success",
        "message": state.get("explanation", "Task completed.")
    }
    return state

# Build the LangGraph State Machine
builder = StateGraph(AgentState)

builder.add_node("intent_router", intent_router_node)
builder.add_node("system_agent", system_agent_node)
builder.add_node("browser_agent", browser_agent_node)
builder.add_node("coding_agent", coding_agent_node)
builder.add_node("general_responder", general_responder_node)

builder.set_entry_point("intent_router")

builder.add_conditional_edges(
    "intent_router",
    route_decision,
    {
        "system_agent": "system_agent",
        "browser_agent": "browser_agent",
        "coding_agent": "coding_agent",
        "general_responder": "general_responder"
    }
)

builder.add_edge("system_agent", END)
builder.add_edge("browser_agent", END)
builder.add_edge("coding_agent", END)
builder.add_edge("general_responder", END)

orchestrator_graph = builder.compile()

async def run_orchestrator(user_prompt: str) -> Dict[str, Any]:
    """Public execution entrypoint for running user requests through the graph."""
    initial_state: AgentState = {
        "user_prompt": user_prompt,
        "target_agent": "general",
        "selected_tool": "none",
        "tool_args": {},
        "explanation": "",
        "execution_result": None,
        "history": []
    }

    final_state = await orchestrator_graph.ainvoke(initial_state)
    
    # Save interaction to MongoDB memory
    tool_used = final_state.get("selected_tool")
    tools_list = [tool_used] if tool_used and tool_used != "none" else []
    
    res = final_state.get("execution_result", {})
    response_msg = res.get("message") if isinstance(res, dict) else str(res)
    
    await db_manager.save_interaction(
        user_prompt=user_prompt,
        agent_response=response_msg or final_state.get("explanation", ""),
        tools_used=tools_list
    )

    return {
        "prompt": user_prompt,
        "target_agent": final_state.get("target_agent"),
        "selected_tool": final_state.get("selected_tool"),
        "explanation": final_state.get("explanation"),
        "result": final_state.get("execution_result")
    }

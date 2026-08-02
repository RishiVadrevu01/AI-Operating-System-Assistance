import json
import logging
import re
import requests
from typing import Dict, Any
from config import config
from .prompts import ORCHESTRATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

def rule_based_fallback(user_prompt: str) -> Dict[str, Any]:
    """Intelligent intent parser for system, browser, search, and dynamic website commands."""
    prompt_lower = user_prompt.lower().strip()

    # 1. Search + Platform Combination Commands (e.g., "open youtube and search KGF trailer", "search X on google")
    if "search" in prompt_lower:
        # Search YouTube
        if "youtube" in prompt_lower:
            query = re.sub(r".*search\s+for|.*search|open\s+youtube\s+and|on\s+youtube|youtube", "", prompt_lower).strip()
            query = re.sub(r"^(for|and)\s+", "", query).strip()
            return {
                "agent": "browser",
                "tool": "search_youtube",
                "args": {"query": query or "trending videos"},
                "explanation": f"Searching YouTube for '{query or 'trending videos'}'."
            }
        # Search Google / Web
        else:
            query = re.sub(r".*search\s+for|.*search|open\s+google\s+and|on\s+google|google", "", prompt_lower).strip()
            query = re.sub(r"^(for|and)\s+", "", query).strip()
            return {
                "agent": "browser",
                "tool": "search_google",
                "args": {"query": query or "latest news"},
                "explanation": f"Searching Google for '{query or 'latest news'}'."
            }

    # 2. Native System Applications
    if "open vs code" in prompt_lower or "open vscode" in prompt_lower or "launch vscode" in prompt_lower:
        return {"agent": "system", "tool": "open_application", "args": {"app_name": "vscode"}, "explanation": "Opening Visual Studio Code."}
    if "open chrome" in prompt_lower or "launch chrome" in prompt_lower:
        return {"agent": "system", "tool": "open_application", "args": {"app_name": "chrome"}, "explanation": "Opening Google Chrome."}
    if "open notepad" in prompt_lower:
        return {"agent": "system", "tool": "open_application", "args": {"app_name": "notepad"}, "explanation": "Opening Notepad."}
    if "open calculator" in prompt_lower or "calc" in prompt_lower:
        return {"agent": "system", "tool": "open_application", "args": {"app_name": "calculator"}, "explanation": "Opening Calculator."}

    # 3. System Folders
    if "downloads" in prompt_lower and ("open" in prompt_lower or "folder" in prompt_lower):
        return {"agent": "system", "tool": "open_folder", "args": {"folder_path": "Downloads"}, "explanation": "Opening Downloads folder."}
    if "documents" in prompt_lower and ("open" in prompt_lower or "folder" in prompt_lower):
        return {"agent": "system", "tool": "open_folder", "args": {"folder_path": "Documents"}, "explanation": "Opening Documents folder."}
    if "desktop" in prompt_lower and ("open" in prompt_lower or "folder" in prompt_lower):
        return {"agent": "system", "tool": "open_folder", "args": {"folder_path": "Desktop"}, "explanation": "Opening Desktop folder."}

    # 4. System Statistics & Metrics
    if any(kw in prompt_lower for kw in ["cpu", "ram", "battery", "stats", "system info", "memory usage"]):
        return {"agent": "system", "tool": "get_system_stats", "args": {}, "explanation": "Checking real-time system performance statistics."}
    if "top process" in prompt_lower or "using the most ram" in prompt_lower or "highest memory" in prompt_lower:
        return {"agent": "system", "tool": "list_running_processes", "args": {"top_n": 5}, "explanation": "Listing processes consuming the most RAM."}

    # 5. Screenshots
    if "screenshot" in prompt_lower or "take screen" in prompt_lower:
        return {"agent": "system", "tool": "take_screenshot", "args": {"filename": "screenshot.png"}, "explanation": "Taking a desktop screenshot."}

    # 6. Dynamic Website Opener for ANY domain (e.g. "open flipkart", "open amazon", "open instagram", "open github", etc.)
    if prompt_lower.startswith(("open ", "launch ", "go to ", "visit ")):
        target = re.sub(r"^(open|launch|go to|visit)\s+", "", prompt_lower).strip()
        # Remove common words like "website", "site", "app"
        target = re.sub(r"\s+(website|site|app)$", "", target).strip()
        
        if target:
            # If target has no domain suffix, default to .com
            domain = target if "." in target else f"{target}.com"
            url = f"https://www.{domain}" if not domain.startswith("www.") else f"https://{domain}"
            return {
                "agent": "browser",
                "tool": "open_url",
                "args": {"url": url},
                "explanation": f"Opening {target.capitalize()} ({url}) in your browser."
            }

    # Default general chat
    return {
        "agent": "general",
        "tool": "none",
        "args": {},
        "explanation": f"I heard: '{user_prompt}'. I am your AI Desktop Assistant Nova, ready to control your applications, files, and system."
    }

async def get_llm_response(user_prompt: str) -> Dict[str, Any]:
    """Query LLM (Ollama / OpenAI API) with automatic fallback."""
    if config.LLM_PROVIDER == "ollama":
        try:
            response = requests.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": config.OLLAMA_MODEL,
                    "prompt": f"{ORCHESTRATOR_SYSTEM_PROMPT}\nUser Command: {user_prompt}\nJSON Output:",
                    "stream": False
                },
                timeout=5
            )
            if response.status_code == 200:
                raw_text = response.json().get("response", "")
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception as e:
            logger.warning(f"Ollama local LLM connection skipped ({e}). Using intelligent rule engine.")

    elif config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            res = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(res.choices[0].message.content)
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}. Falling back to rule engine.")

    # Rule-based fallback if offline or response fails
    return rule_based_fallback(user_prompt)

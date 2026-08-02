import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Assistant Metadata
    ASSISTANT_NAME: str = os.getenv("ASSISTANT_NAME", "Nova")
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "openai"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:latest") # default model name
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # MongoDB Settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "desktop_ai_db")

    # System Settings & Directories
    USER_HOME: Path = Path.home()
    DOWNLOADS_DIR: Path = USER_HOME / "Downloads"
    DOCUMENTS_DIR: Path = USER_HOME / "Documents"
    DESKTOP_DIR: Path = USER_HOME / "Desktop"

    # Risk Levels for Executions
    # Low: Auto-executed without user prompt
    # Medium: Warning/Confirmation prompt recommended
    # High: Restricted or Explicit Human Approval required
    RISK_LEVELS = {
        "OPEN_APP": "LOW",
        "OPEN_URL": "LOW",
        "SYSTEM_INFO": "LOW",
        "SCREENSHOT": "LOW",
        "SEARCH_WEB": "LOW",
        "CREATE_FILE": "LOW",
        "MOVE_FILE": "LOW",
        "RUN_COMMAND": "MEDIUM",
        "DELETE_FILE": "MEDIUM",
        "SHUTDOWN": "HIGH",
    }

config = Config()

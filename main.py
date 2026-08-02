import asyncio
import logging
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from config import config
from db.mongo import db_manager
from agents.orchestrator import run_orchestrator
from ui.desktop import start_interactive_cli

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"{config.ASSISTANT_NAME} - AI Operating System Assistant",
    version="1.0.0",
    description="REST API and Backend Agent for Windows AI Operating System Assistant"
)

class CommandRequest(BaseModel):
    command: str

class MemoryRequest(BaseModel):
    key: str
    value: Any
    category: Optional[str] = "general"

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Nova AI OS Assistant services...")
    await db_manager.connect()

@app.get("/")
async def root():
    return {
        "status": "online",
        "assistant_name": config.ASSISTANT_NAME,
        "llm_provider": config.LLM_PROVIDER,
        "mongodb_connected": db_manager.is_connected
    }

@app.post("/execute")
async def execute_command(req: CommandRequest):
    if not req.command.strip():
        raise HTTPException(status_code=400, detail="Command string cannot be empty")
    try:
        result = await run_orchestrator(req.command)
        return result
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory")
async def save_memory(req: MemoryRequest):
    try:
        await db_manager.save_memory(key=req.key, value=req.value, category=req.category)
        return {"status": "success", "message": f"Saved memory key '{req.key}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
async def get_memories(category: Optional[str] = None):
    try:
        memories = await db_manager.get_memories(category=category)
        return {"status": "success", "memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        asyncio.run(start_interactive_cli())
    else:
        import uvicorn
        logger.info("Starting FastAPI server on http://127.0.0.1:8000 ...")
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

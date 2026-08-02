# 🤖 Nova - AI Operating System Assistant

**Nova** is a native AI Desktop Operating System Assistant built using Python, LangGraph multi-agent orchestration, FastAPI, Playwright, PyAutoGUI, and MongoDB. It bridges local LLMs (Qwen / Llama via Ollama or OpenAI) directly to your Windows desktop, enabling natural voice/text control over your computer.

---

## 🌟 Key Features

* **🗣️ Voice & Text Interface:** Talk or type commands directly to Nova.
* **🧠 Multi-Agent Architecture (LangGraph):** State-machine router that dynamically delegates tasks to specialized sub-agents:
  * **System Agent:** Opens applications, opens folders, captures screenshots, monitors CPU/RAM/Battery, lists memory-heavy processes, schedules shutdowns.
  * **Browser Agent:** Launches web pages, performs YouTube & Google searches, automates web navigation via Playwright.
  * **Coding Agent:** Generates files, creates project structures, executes terminal commands.
* **💾 Persistent Memory (MongoDB):** Asynchronously logs all interactions, user preferences, and project shortcuts into MongoDB (with dynamic in-memory fallback).
* **⚡ FastAPI Backend:** Exposes clean REST API endpoints (`/execute`, `/memory`) for background service & desktop UI integration.
* **🛡️ Security & Permission Tiers:** Low/Medium/High risk classifications for system calls.

---

## 🏗️ Architecture

```
User Command (Voice / Text / API)
              │
              ▼
    AI Orchestrator (LangGraph)
    Intent Router & Model Selector
              │
  ┌───────────┼──────────────┬──────────────┐
  │           │              │              │
System     Browser        Coding         General
Agent       Agent          Agent        Responder
  │           │              │              │
Apps/Files  Playwright    Files/Terminal   Direct Chat
  │           │              │              │
  └───────────┴──────────────┴──────────────┘
              │
              ▼
   MongoDB Persistent Memory
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone the repository and install the dependencies:
```bash
cd AI-Operating-System-Assistance
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and adjust your preferences:
```bash
cp .env.example .env
```

To run with local LLMs via Ollama:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest
```

To run with MongoDB (Local or Atlas):
```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=desktop_ai_db
```
*(Note: If MongoDB is offline, Nova automatically uses an in-memory session database.)*

---

## 💻 Usage Modes

### Mode 1: Interactive Desktop CLI
Run the assistant directly in your terminal:
```bash
python main.py --cli
```

**Try commands like:**
* `"Open VS Code"`
* `"Open YouTube and search for FastAPI tutorials"`
* `"Open Downloads folder"`
* `"What is my CPU usage?"`
* `"Take a screenshot"`
* `"What is using the most RAM?"`

### Mode 2: FastAPI REST API Server
Start the background API server:
```bash
python main.py
```
Open your browser at `http://127.0.0.1:8000/docs` to view the interactive API documentation.

#### Example API Execution Request:
```json
POST http://127.0.0.1:8000/execute
Content-Type: application/json

{
  "command": "Open Downloads folder"
}
```

---

## 📂 Project Structure

```
AI-Operating-System-Assistance/
├── config.py                 # Configuration & environment variables
├── requirements.txt          # Package dependencies
├── main.py                   # FastAPI app & CLI entry point
├── db/
│   └── mongo.py              # MongoDB async manager & in-memory fallback
├── llm/
│   ├── provider.py           # LLM provider (Ollama / OpenAI / Fallback)
│   └── prompts.py            # Intent & tool prompts
├── tools/
│   ├── system.py             # App, folder, processes, screenshot & stats tools
│   ├── browser.py            # Web search & Playwright navigation tools
│   └── coding.py             # File creation & terminal execution tools
├── agents/
│   ├── state.py              # LangGraph state definition
│   ├── system_agent.py       # System node runner
│   ├── browser_agent.py      # Browser node runner
│   ├── coding_agent.py       # Coding node runner
│   └── orchestrator.py       # Main LangGraph graph state machine
├── speech/
│   ├── stt.py                # Speech-to-text integration
│   └── tts.py                # Text-to-speech audio feedback
└── ui/
    └── desktop.py            # Desktop CLI runner
```

---

## 📜 License
MIT License. Built for autonomous AI Operating System agent research.
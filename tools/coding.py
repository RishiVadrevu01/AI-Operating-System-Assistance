import os
import subprocess
from pathlib import Path
from typing import Dict, Any

def create_folder(folder_path: str) -> Dict[str, Any]:
    """Create a directory if it does not exist."""
    try:
        path = Path(folder_path)
        path.mkdir(parents=True, exist_ok=True)
        return {"status": "success", "message": f"Folder created at '{path.absolute()}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to create folder '{folder_path}': {str(e)}"}

def create_file(file_path: str, content: str = "") -> Dict[str, Any]:
    """Create a file with specified content."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return {"status": "success", "message": f"File created at '{path.absolute()}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to create file '{file_path}': {str(e)}"}

def execute_terminal_command(command: str, cwd: str = ".") -> Dict[str, Any]:
    """Execute a safe shell/terminal command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"status": "error", "message": f"Command execution failed: {str(e)}"}

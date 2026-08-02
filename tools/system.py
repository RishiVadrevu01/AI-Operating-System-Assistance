import os
import subprocess
import psutil
import logging
from pathlib import Path
from typing import Dict, Any, List
from config import config

logger = logging.getLogger(__name__)

# Common app paths on Windows
APP_MAP = {
    "vscode": ["code", "Code.exe"],
    "vs code": ["code", "Code.exe"],
    "chrome": ["chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "explorer": ["explorer.exe"],
    "spotify": ["spotify.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"]
}

def open_application(app_name: str) -> Dict[str, Any]:
    """Launch a desktop application by name."""
    clean_name = app_name.lower().strip()
    executable_candidates = APP_MAP.get(clean_name, [clean_name])

    for exec_item in executable_candidates:
        try:
            subprocess.Popen(exec_item, shell=True)
            return {"status": "success", "message": f"Successfully launched {app_name}"}
        except Exception as e:
            logger.debug(f"Could not launch using {exec_item}: {e}")

    try:
        os.system(f"start {clean_name}")
        return {"status": "success", "message": f"Attempted system start for '{app_name}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to launch '{app_name}': {str(e)}"}

def open_folder(folder_path: str) -> Dict[str, Any]:
    """Open a folder in Windows File Explorer."""
    path_lower = folder_path.lower().strip()
    target_path = None

    if "download" in path_lower:
        target_path = config.DOWNLOADS_DIR
    elif "document" in path_lower:
        target_path = config.DOCUMENTS_DIR
    elif "desktop" in path_lower:
        target_path = config.DESKTOP_DIR
    else:
        target_path = Path(folder_path)

    if not target_path.exists():
        try:
            target_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"status": "error", "message": f"Path '{target_path}' does not exist and could not be created: {e}"}

    try:
        os.startfile(str(target_path))
        return {"status": "success", "message": f"Opened folder: {target_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to open folder '{target_path}': {str(e)}"}

def get_system_stats() -> Dict[str, Any]:
    """Get real-time CPU, RAM, Disk, and Battery usage statistics."""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        battery = psutil.sensors_battery()

        stats = {
            "cpu_percent": cpu_percent,
            "ram_used_gb": round(ram.used / (1024 ** 3), 2),
            "ram_total_gb": round(ram.total / (1024 ** 3), 2),
            "ram_percent": ram.percent,
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
            "disk_percent": disk.percent,
            "battery_percent": battery.percent if battery else "N/A",
            "power_plugged": battery.power_plugged if battery else "N/A"
        }
        return {"status": "success", "data": stats}
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve system stats: {str(e)}"}

def take_screenshot(filename: str = "screenshot.png") -> Dict[str, Any]:
    """Capture the active desktop screen."""
    try:
        import pyautogui
        save_dir = config.DOCUMENTS_DIR / "AssistantScreenshots"
        save_dir.mkdir(parents=True, exist_ok=True)
        filepath = save_dir / filename
        
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        return {"status": "success", "message": f"Screenshot saved to {filepath}", "path": str(filepath)}
    except Exception as e:
        return {"status": "error", "message": f"Screenshot failed: {str(e)}"}

def list_running_processes(top_n: int = 5) -> Dict[str, Any]:
    """List the top processes consuming the most RAM."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "memory_mb": round(mem_mb, 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        sorted_procs = sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:top_n]
        return {"status": "success", "top_processes": sorted_procs}
    except Exception as e:
        return {"status": "error", "message": f"Failed to list processes: {str(e)}"}

def shutdown_system(delay_seconds: int = 60) -> Dict[str, Any]:
    """Schedule a system shutdown (Requires confirmation)."""
    try:
        os.system(f"shutdown /s /t {delay_seconds}")
        return {"status": "success", "message": f"System scheduled to shutdown in {delay_seconds} seconds."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to schedule shutdown: {str(e)}"}

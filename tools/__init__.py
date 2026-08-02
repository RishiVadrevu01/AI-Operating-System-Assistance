from .system import (
    open_application,
    open_folder,
    get_system_stats,
    take_screenshot,
    list_running_processes,
    shutdown_system
)
from .browser import open_url, search_youtube, search_google
from .coding import create_file, create_folder, execute_terminal_command

__all__ = [
    "open_application",
    "open_folder",
    "get_system_stats",
    "take_screenshot",
    "list_running_processes",
    "shutdown_system",
    "open_url",
    "search_youtube",
    "search_google",
    "create_file",
    "create_folder",
    "execute_terminal_command"
]

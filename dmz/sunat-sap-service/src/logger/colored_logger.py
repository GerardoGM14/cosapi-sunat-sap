from typing import Optional, Literal
import os
from datetime import datetime
import re


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLACK = '\033[30m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    GRAY = '\033[90m'
    BRIGHT_GRAY = '\033[37m'


class ColoredLogger:
    enableLogGlobal = True
    LOG_DIR = "logs"
    LOG_FILE = "app.log"
    
    def __init__(self, disableModule: Optional[bool] = False):
        self.disableModule = disableModule
        self._ensure_log_dir()
        
    def _ensure_log_dir(self):
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)

    def _remove_ansi_codes(self, text: str) -> str:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    def _write_to_file(self, message: str):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            clean_message = self._remove_ansi_codes(message)
            with open(os.path.join(self.LOG_DIR, self.LOG_FILE), "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {clean_message}\n")
        except Exception:
            pass
        
    def log(
        self,
        message: str,
        color: Optional[Colors] = Colors.BRIGHT_WHITE,
        force_show: Optional[bool] = False,
        show: Optional[bool] = True,
        send_to_socket: Optional[bool] = True
    ):
        if not ColoredLogger.enableLogGlobal:
            return

        if self.disableModule and not force_show:
            return
            
        if show:
            print(f"{color}{message}{Colors.RESET}")
            self._write_to_file(message)
            
        if send_to_socket:
            try:
                from src.socket_client.manager import socket_manager
                from src.schemas.ISocket import EmitEvent
                from src.utils.date_current import dateCurrent
                if socket_manager.socket_client and socket_manager.socket_client.is_connected:
                    # Clean ansi codes for socket message
                    clean_msg = self._remove_ansi_codes(message)
                    socket_manager.emit(EmitEvent.LOG, {'message': clean_msg, 'date': dateCurrent()})
            except ImportError:
                pass 
            except Exception:
                pass

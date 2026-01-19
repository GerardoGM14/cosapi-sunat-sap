from typing import Optional, Literal


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
    
    def __init__(self, disableModule: Optional[bool] = False):
        self.disableModule = disableModule  
        
    def log(
        self,
        message: str,
        color: Optional[Colors] = Colors.BRIGHT_WHITE,
        force_show: Optional[bool] = False,
        show: Optional[bool] = True,
    ):
        if not ColoredLogger.enableLogGlobal:
            return

        if self.disableModule and not force_show:
            return
            
        if show:
            print(f"{color}{message}{Colors.RESET}")

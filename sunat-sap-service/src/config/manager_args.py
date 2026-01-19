import os
import json
from typing import Optional
from dotenv import load_dotenv
from src.utils.args_console import get_args_console
from src.utils.args_env import get_args_env
from src.schemas.IConfig import IArgs
from src.logger.colored_logger import ColoredLogger, Colors

load_dotenv()

logger = ColoredLogger()

def get_args() -> Optional[IArgs]:
    try:
        config_method = os.getenv('CONFIG_METHOD', 'env') 

        args: IArgs
        if config_method == 'console':
            args = get_args_console()
        else:
            args = get_args_env()
        
        logger.log(
            json.dumps(args, indent=4, ensure_ascii=False),
            color=Colors.BRIGHT_CYAN,
            show=False
        )
        return args
    except Exception as e:
        logger.log(f'🔴 Error con los argumentos: {e}', color=Colors.RED)
        return

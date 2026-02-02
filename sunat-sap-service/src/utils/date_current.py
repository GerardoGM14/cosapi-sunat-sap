from datetime import datetime

def dateCurrent() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

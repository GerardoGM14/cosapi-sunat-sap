import sys
import os

# Añadir el directorio actual al path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.watcher import main

if __name__ == "__main__":
    main()

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.sync_api import Page
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger()


class DebugIMG:
    def __init__(
        self,
        page: Page,
        tipo_venta_compra: Optional[str] = None,
        ruc: Optional[str | int] = None,
    ):
        self.tipo_venta_compra = tipo_venta_compra
        self.ruc = ruc
        self.page = page

    async def saveImg(self, name_img: str):
        date = datetime.now().strftime('%d-%m-%Y_%H-%M')
        tipo = (self.tipo_venta_compra or "sin_tipo").lower()
        ruc = str(self.ruc or "sin_ruc")
        path_dir = Path(sys.executable).parent / 'DebugValidacionesIMG' / tipo / ruc
        path_dir.mkdir(parents=True, exist_ok=True)
        
        full_path = path_dir / f"{name_img}_{date}.jpg"
        
        # await self.page.screenshot(path=full_path)
        logger.log(f'📷 [Debug] {full_path}', color=Colors.BRIGHT_CYAN, show=False)
        return full_path

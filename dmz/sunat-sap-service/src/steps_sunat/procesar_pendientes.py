import os
from playwright.async_api import Page
from playwright.sync_api import FrameLocator
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger(disableModule=False)


async def procesar_pendientes(
    frame: FrameLocator,
    page: Page,
    ruc: str,
    year: int = 2024,
    month: int = 4,
    folder: str = None,
    card: str = "Pendientes"
) -> IReturn:

    logger.log(f"📁 Ruta de descargas: {folder}", color=Colors.MAGENTA)
    os.makedirs(folder, exist_ok=True)

    try:
        exportar = frame.locator('//button[contains(text(), "Exportar a Excel")]')
        await exportar.scroll_into_view_if_needed()
        
        async with page.expect_download() as download_info:
            await exportar.click()
        
        download = await download_info.value
        pathfile = f"{folder}/{card}_{ruc}_{year}_{str(month).zfill(2)}.xlsx"
        await download.save_as(pathfile)
        
        logger.log(f'📚 Se dió click para descargar {card.upper()} correctamente.', color=Colors.CYAN)
        
        return {
            'success': True,
            'message': f'✅ Se descargó el archivo excel de {card.upper()}',
            'error_system': False,
            'file_path_sunat': pathfile
        }
    except Exception as e:
        logger.log(f'❌ Error al procesar {card.upper()}: {type(e).__name__} - {e}', color=Colors.RED)
        return {
            'success': False,
            'message':  f'❌ Error al procesar {card.upper()}: {type(e).__name__} - {e}',
            'error_system': True
        }

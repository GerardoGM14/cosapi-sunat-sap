import os
import asyncio
from src.schemas.IReturn import IReturn
from playwright.async_api import FrameLocator, Page
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger()


async def descargar_excel(page: Page, frame: FrameLocator, folder: str, code_sociedad: str) -> IReturn:
    try:
        await frame.locator(
            "button:has-text('Descargar Excel')"
        ).wait_for(state="visible", timeout=5000)

        os.makedirs(folder, exist_ok=True)

        async with page.expect_download() as download_info:
            await frame.locator(
                "button:has-text('Descargar')"
            ).click()

        download = await download_info.value

        filename_original = download.suggested_filename
        new_filename = f'{code_sociedad}_{filename_original}'
        file_path = os.path.join(folder, new_filename)
        await download.save_as(file_path)

        msg = f'✅ Archivo guardado en {file_path}'
        logger.log(msg, Colors.GREEN, force_show=True)
        await asyncio.sleep(2)
        return {
            "success": True,
            "error_system": False,
            "message": msg,
            "frame": frame,
            "file_path_sap": file_path,
        }

    except Exception as e:
        msg = f"❌ Error en descargar: {e}"
        logger.log(msg, Colors.RED, force_show=True)
        return {
            "success": False,
            "error_system": True,
            "message": msg,
            "frame": None
        }

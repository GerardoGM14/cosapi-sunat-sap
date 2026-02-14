import asyncio
from playwright.sync_api import FrameLocator
from playwright.async_api import TimeoutError
from src.logger.colored_logger import ColoredLogger, Colors
from src.schemas.IReturn import IReturn

logger = ColoredLogger(disableModule=False)


async def validar_filtros(frame: FrameLocator) -> IReturn:
    try:
        try:
            texto_warning = frame.locator('(//div[@role="alertdialog" and .//span[contains(text(), "No se encontraron resultados")]]//button)[1]')
            await texto_warning.wait_for(timeout=8000, state="visible")
            await texto_warning.click()

            logger.log("⚠️ No Se encontraron resultados", Colors.GREEN, force_show=True)
            
            await asyncio.sleep(1)
            
            return {
                'success': False,
                'error_system': False,
                'message': "No se encontraron resultados",
                'frame': frame
            }
        except TimeoutError as e:
            logger.log(f"TimeoutError en validar_filtros: {e}", Colors.YELLOW, show=False)
            pass

        await frame.locator(
            "xpath=//table[contains(@id, 'idTableFacturas-table')]/tbody/tr[contains(@class, 'sapUiTableRow')]"
        ).first.wait_for(timeout=5000, state="visible")

        first_row_text = await frame.locator(
            "xpath=//table[contains(@id, 'idTableFacturas-table')]/tbody/tr[contains(@class, 'sapUiTableRow')][1]"
        ).text_content()

        logger.log(f"TEXTO = {first_row_text}", Colors.CYAN)

        if first_row_text is None or not first_row_text.strip():
            msg = 'No se encontraron resultados en la primera fila'
            logger.log(msg, color=Colors.YELLOW, force_show=True)
            return {
                'success': False,
                'error_system': False,
                'message': msg,
                'frame': frame
            }
        
        msg = 'Se encontraron resultados en la primera fila'
        logger.log(msg, color=Colors.GREEN, force_show=True)
        return {
            'success': True,
            'error_system': False,
            'message': msg,
            'frame': frame
        }
    except Exception as e:
        msg = f'Error en validar_filtros: {e}'
        logger.log(msg, color=Colors.RED, force_show=True)
        return {
            'success': False,
            'error_system': True,
            'message': msg,
            'frame': None
        }

from playwright.async_api import Page, TimeoutError
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger(disableModule=True)


async def cerrar_modales_iniciales(page: Page) -> IReturn:
    try:
        frame = page.frame_locator('iframe[name="ifrVCE"]')
        
        try:
            await page.wait_for_selector('#btnFinalizarValidacionDatos', state="visible", timeout=2000)
            boton = frame.locator("#btnFinalizarValidacionDatos")
        except TimeoutError:
            return {
                'success': True,
                'message': '✅ No se encontró la ventana emergente o el frame. Es posible que no haya nada que cerrar.',
                'error_system': False
            }

        botones = ["btnFinalizarValidacionDatos", "btnCerrar"]
        
        for boton_id in botones:
            try:
                boton = frame.locator(f"#{boton_id}")
                
                if await boton.is_visible():
                    await boton.click(timeout=2000, force=True) 
            except TimeoutError:
                logger.log(f"Botón '{boton_id}' no apareció o no fue clickeable.", color=Colors.YELLOW)
            except Exception as e:
                logger.log(f"Error al intentar hacer click en '{boton_id}': {e}", color=Colors.RED)

        msg = '✅ Se cerraron ventana(s) emergente(s).'
        logger.log(msg, color=Colors.GREEN, force_show=True)
        return {
            'success': True,
            'message': msg,
            'error_system': False
        }

    except Exception as e:
        msg = f'❌ Ocurrió un error inesperado al cerrar ventanas emergentes: {type(e).__name__}'
        logger.log(msg, color=Colors.RED, force_show=True)
        return {
            'success': False,
            'message': msg,
            'error_system': True
        }
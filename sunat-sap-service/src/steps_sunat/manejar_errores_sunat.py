import asyncio
from playwright.async_api import Page, TimeoutError
from playwright.sync_api import FrameLocator
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger()


async def manejar_errores_sunat(frame: FrameLocator, intento: int = 0, timeout: int = 3) -> bool:
    
    logger.log(f"\n🔍 Buscando modales de error en intento {intento + 1}...", color=Colors.YELLOW)

    xpath_any_error = (
        "//ngb-modal-window["
        ".//p[contains(text(), 'Error del Servidor')] or "
        ".//div[contains(text(), '(Status 504)')]"
        "]"
    )

    try:
        await frame.locator(xpath_any_error).wait_for(state="attached", timeout=timeout * 1000)
        logger.log(f"⚠️ Se detectaron modales de error. Intentando cerrarlos... [Intento {intento + 1}]", color=Colors.YELLOW)
    except TimeoutError:
        logger.log(f"✅ SUNAT OK: Sin errores modales detectados [Intento {intento + 1}]\n", color=Colors.GREEN)
        return False
    except Exception as e:
        logger.log(f"✅ SUNAT OK: Error al buscar modales (probablemente no existen): {e}", color=Colors.GREEN)
        return False

    modals_closed_count = 0
    
    while True:
        modals_locator = frame.locator(xpath_any_error)
        count = await modals_locator.count()
        
        if count == 0:
            if modals_closed_count > 0:
                logger.log("🔍 No se encontraron más modales de error.", color=Colors.GREEN)
            break
        
        top_modal = modals_locator.last
        
        try:
            error_type = "desconocido"
            if await top_modal.locator("//p[contains(text(), 'Error del Servidor')]").count() > 0:
                error_type = "Error del Servidor"
            elif await top_modal.locator("//div[contains(text(), '(Status 504)')]").count() > 0:
                error_type = "Tiempo de Espera (504)"

            logger.log(f"🚨 Se encontraron {count} modales. El superior es de tipo: '{error_type}'.", color=Colors.YELLOW)

            boton_aceptar = top_modal.locator("//button[contains(text(), 'Aceptar')]")
            
            logger.log(f"🖱️ Haciendo clic en 'Aceptar' del modal '{error_type}'...", color=Colors.YELLOW)
            
            await boton_aceptar.dispatch_event("click")
            
            modals_closed_count += 1
            await asyncio.sleep(1) 
            
        except Exception as e:
            logger.log(f"⚠️ No se pudo hacer clic en el botón del modal. Error: {e}", color=Colors.YELLOW)
            break

    if modals_closed_count > 0:
        logger.log(f'⚠️ Se cerraron {modals_closed_count} modales de error. Reintentando... [Intento {intento + 1}]\n', color=Colors.YELLOW)
        return True
    else:
        logger.log("🤔 Se detectó un modal inicialmente, pero no se pudo cerrar ninguno.\n", color=Colors.YELLOW)
        return True

from playwright.sync_api import FrameLocator
from src.utils.procesar_fecha import procesar_fecha
from src.logger.colored_logger import ColoredLogger, Colors
from src.schemas.IReturn import IReturn

logger = ColoredLogger(disableModule=True)


async def filtros(fecha: str, code_sociedad: str, frame: FrameLocator) -> IReturn:
    try:
        result = procesar_fecha(fecha)
        
        if isinstance(result, str):
            return {
                "success": False,
                "error_system": False,
                "message": result,
                "frame": None
            }

        if not code_sociedad:
            return {
                "success": False,
                "error_system": False,
                "message": "El código de sociedad es requerido",
                "frame": None
            }

        fecha_inicio, fecha_fin = result
        
        fecha_insert =f'{fecha_inicio} – {fecha_fin}'

        fecha_input = frame.locator('[id$="--idFechaEmision-inner"]')
        await fecha_input.wait_for(state="visible", timeout=10000)
        await fecha_input.fill(fecha_insert)
        
        arrow_locator = frame.locator('[id$="--IdSociedadesFiltros-arrow"]')
        await arrow_locator.wait_for(state="visible", timeout=10000)
        
        arrow_selector = '[id$="--IdSociedadesFiltros-arrow"]'
        logger.log("[Proceso] Abriendo el desplegable de Sociedades...", Colors.CYAN)
        await frame.locator(arrow_selector).click()

        ul_id = "application-reportecontabilidad-display-component---Home--IdSociedadesFiltros-popup-list-listUl"
        list_container = frame.locator(f'ul[id$="{ul_id}"]')

        items = list_container.locator("li.sapMLIB")
        count = await items.count()
        for i in range(count):
            item = items.nth(i)
            codigo = await item.locator('[id$="-infoText"]').inner_text()
            empresa = await item.locator('[id$="-titleText"]').inner_text()
            logger.log(f"Item {i+1}/{count}: {codigo.strip()} - {empresa.strip()}", Colors.BRIGHT_MAGENTA)
        
        await list_container.wait_for(state="visible", timeout=15000)

        target_item_selector = f'li.sapMLIB:has(span[id$="-infoText"]:text-is("{code_sociedad}"))'
        target_locator = list_container.locator(target_item_selector)

        if await target_locator.count() > 0:
            logger.log(f"✅ Sociedad {code_sociedad} encontrada. Desplazando y haciendo clic...", Colors.GREEN)
            
            await target_locator.scroll_into_view_if_needed()
            await target_locator.click()
            
            logger.log(f"✅ Clic realizado en sociedad: {code_sociedad}", Colors.GREEN)
        else:
            logger.log(f"⚠️ No se encontró {code_sociedad} por selector directo, verificando items...", Colors.YELLOW)
            items_locator = list_container.locator("li.sapMLIB")
            count = await items_locator.count()
            encontrado = False
            
            for i in range(count):
                item = items_locator.nth(i)
                codigo_actual = await item.locator('[id$="-infoText"]').inner_text()
                if codigo_actual.strip() == code_sociedad.strip():
                    await item.scroll_into_view_if_needed()
                    await item.click()
                    encontrado = True
                    logger.log(f"✅ Seleccionado mediante búsqueda manual: {code_sociedad}", Colors.GREEN)
                    break
            
            if not encontrado:
                logger.log(f"❌ Error: El código de sociedad {code_sociedad} no existe en la lista.", Colors.RED, force_show=True)
                await arrow_locator.click()
                return IReturn(
                    success=False,
                    message=f"El código de sociedad {code_sociedad} no existe en la lista.",
                    error_system=False,
                    frame=None
                )

        buscar_button = frame.locator('//button[.//text()[contains(., "Buscar")]]')
        await buscar_button.wait_for(state="visible", timeout=10000)
        await buscar_button.click()

        logger.log("✅ Clic realizado en el botón 'Buscar'.", Colors.GREEN)
        msg = "✅ Filtros aplicados con éxito."
        logger.log(msg, Colors.GREEN, force_show=True)
        return IReturn(
            success=True,
            message=msg,
            error_system=False,
            frame=frame
        )
    except Exception as e:
        msg = f"❌ ERROR en el flujo de Filtros: {e}"
        logger.log(msg, Colors.RED, force_show=True)
        return IReturn(
            success=False,
            message=msg,
            error_system=True,
            frame=None
        )

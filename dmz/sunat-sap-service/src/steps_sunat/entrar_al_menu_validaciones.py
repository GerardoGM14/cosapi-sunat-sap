import asyncio
from playwright.async_api import Page, TimeoutError
from src.debug.debug_img import DebugIMG
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger(disableModule=True)


async def entrar_al_menu_validaciones(page: Page, tipo_venta_compra: str = 'no_especificado', ruc: str = 'no_ruc') -> IReturn:
    
    debug = DebugIMG(
        page=page, 
        tipo_venta_compra=tipo_venta_compra,
        ruc=ruc
    )

    try:
        default_timeout = 60000

        selectores = [
            '//div[@id="divOpcionServicio2"]',
            '(//li[@data-id2=61])[1]',
            '(//li[@id="nivel2_61_1"])[1]',
            '(//li[@id="nivel3_61_1_1"])[1]',
            '(//li[@id="nivel4_61_1_1_1_1"])[1]'
        ]

        for selector in selectores:
            el = page.locator(selector)
            await el.wait_for(state="visible", timeout=default_timeout)
            await el.click()

        ultimo_click_exitoso = False
        max_reintentos = 4
        
        for intento in range(max_reintentos):
            try:
                logger.log(f"🔄 Intento {intento + 1} de {max_reintentos} para el último menú...")

                ultimo_elemento = page.locator('(//li[@id="nivel4_61_1_1_1_1"])[1]')
                await ultimo_elemento.click(timeout=5000)
                await asyncio.sleep(2.5)
                logger.log("⏳ Esperando que el iframe se cargue...")
                
                iframe_selector = "#iframeApplication"
                iframe = page.frame_locator(iframe_selector)
                
                body = iframe.locator("body")
                await body.wait_for(state="attached", timeout=20000)
                
                texto_body = await body.inner_text()
                texto_body = texto_body.strip()
                
                if not texto_body:
                    if intento < max_reintentos - 1:
                        await debug.saveImg(f"iframe_vacio_intento_{intento + 1}_{tipo_venta_compra}_{ruc}")
                        await asyncio.sleep(2.5)
                    raise Exception("⚠️ Iframe cargado pero vacío")
                
                ultimo_click_exitoso = True
                logger.log("✅ Iframe cargado correctamente")
                break
                
            except (TimeoutError, Exception) as e:
                logger.log(f"⚠️ Intento {intento + 1} falló: {str(e)}")
                if intento < max_reintentos - 1:

                    logger.log(f"⚠️ Intento {intento + 1} falló: {str(e)}")
                else:
                    await debug.saveImg(f"ultimo_click_fallido_{intento + 1}_{tipo_venta_compra}_{ruc}")
                    logger.log(f"❌ Todos los intentos fallaron después de {max_reintentos} reintentos")

        if not ultimo_click_exitoso:
            msg = '✖️ Se agotaron los intentos para entrar al menú de validaciones'
            logger.log(msg, color=Colors.YELLOW, force_show=True)
            return {
                'success': False,
                'message': msg,
                'error_system': True
            }
        
        msg = '📂 Navegado al menú de Confirmación'
        logger.log(msg, color=Colors.BRIGHT_GREEN, force_show=True)
        await asyncio.sleep(2.5)
        return {
            'success': True,
            'message': msg,
            'error_system': False,
            'frame': iframe
        }
    except Exception as e:
        await debug.saveImg(f"error_ultimo_click_{tipo_venta_compra}_{ruc}")
        msg = f'❌ No se pudo abrir el menú de Confirmación: {type(e).__name__}'
        logger.log(msg, color=Colors.BRIGHT_RED, force_show=True)
        return {
            'success': False,
            'message': msg,
            'error_system': True
        }

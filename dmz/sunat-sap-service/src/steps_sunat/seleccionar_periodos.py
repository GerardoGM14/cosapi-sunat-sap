import asyncio
from playwright.sync_api import FrameLocator
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
from src.steps_sunat.manejar_errores_sunat import manejar_errores_sunat
from src.utils.overlay import esperar_overlay_desaparezca
from src.utils.spinner import esperar_spinner_desaparezca
from src.utils.numero_a_mes import numero_a_mes

logger = ColoredLogger(disableModule=False)


async def seleccionar_periodos(year: int, month: int, compras_o_ventas: str, ruc: str, frame: FrameLocator) -> IReturn:
    try:
        logger.log(f'🔍 Porcesando RUC {ruc}', color=Colors.CYAN)
        timeout_standard = 5000 

        overlay = await esperar_overlay_desaparezca(frame)
        if not overlay['success']:
            return {
                'success': False,
                'error_system': True,
                'message': overlay['message']
            }

        await manejar_errores_sunat(frame=frame, intento=1)
        
        yearSelected = False
        monthSelected = False
        
        for intento in range(3):
            logger.log(
                f'\n🔍 Intentando seleccionar periodos para {compras_o_ventas} - [Año {year}] - [Mes {month}] - Intento {intento + 1}',
                color=Colors.CYAN
            )
            try:
                if not yearSelected:
                    group = frame.locator("div.btn-group.btn-temporada")
                    btn_year = group.locator(f"[id='{year}']")
                    await btn_year.wait_for(state="visible", timeout=timeout_standard)
                    await btn_year.click(timeout=timeout_standard, force=True)
                    try:
                        await frame.locator(f'//h4[text()={year}]').wait_for(state="visible", timeout=timeout_standard)
                        yearSelected = True
                        logger.log(f'📅 Año {year} seleccionado', color=Colors.GREEN)
                    except TimeoutError:
                        logger.log(f'⚠️ Año {year} no seleccionado en intento {intento + 1}', color=Colors.YELLOW)
                        continue
                    
                await asyncio.sleep(2)
                
                if not monthSelected:
                    MES = numero_a_mes(num_month=month)
                    selector_month = f'button[value="{MES["abreviatura_opt"]}"]'
                    btn_month = frame.locator(selector_month)
                    await btn_month.wait_for(state="visible", timeout=timeout_standard)
                    await btn_month.click(timeout=timeout_standard, force=True)
                    logger.log(f"📅 Haciendo clic en mes ({MES['abreviatura_opt']})...", color=Colors.BRIGHT_CYAN)
                    try:
                        active_month_selector = f'button.active[value="{MES["abreviatura_opt"]}"]'
                        
                        logger.log(f"🔍 Esperando a que ({MES['abreviatura_opt']}) se active...", color=Colors.MAGENTA)
                        await frame.locator(active_month_selector).wait_for(state="visible", timeout=timeout_standard)
                        monthSelected = True
                        logger.log(f'📅  Mes {MES["nombre_completo_mes_opt"]} ({MES["abreviatura_opt"]}) seleccionado', color=Colors.GREEN)
                    except TimeoutError:
                        logger.log(f'⚠️ Mes {MES["nombre_completo_mes_opt"]} ({MES["abreviatura_opt"]}) no seleccionado en intento {intento + 1}', color=Colors.YELLOW)
                        continue

                overlay = await esperar_overlay_desaparezca(frame)
                if not overlay['success']:
                    logger.log(f'Overlay no desapareció en intento {intento + 1}', color=Colors.YELLOW)
                    continue

            except Exception as e:
                logger.log(f'⚠️ Error en intento {intento + 1}: {e}', color=Colors.YELLOW)
                continue

            if not await manejar_errores_sunat(frame=frame, intento=intento):
                break
        else:
            return {
                'success': False,
                'message': "⚠️ Error SUNAT: Servicios no disponibles después de 3 intentos.",
                'error_system': True
            }

        tipo = 2 if "compra" in compras_o_ventas.lower() else 1 if "venta" in compras_o_ventas.lower() else 0
        texto_esperado = "Mis comprobantes de Compra" if tipo == 2 else "Mis comprobantes de Venta"
        
        logger.log(f'🍕 Texto esperado: {texto_esperado}', color=Colors.BRIGHT_MAGENTA)
        
        if tipo == 0:
            return {
                'success': False,
                'message': '🧱 Solo se puede seleccionar Compras o Ventas',
                'error_system': False
            }

        await asyncio.sleep(1)

        pestaña = frame.locator(f'(//ul/li[@class="nav-item"]//a)[{tipo}]')
        await pestaña.wait_for(state="visible", timeout=timeout_standard)

        logger.log(f"🍕 Pestaña {tipo} visible: {await pestaña.is_visible()}", color=Colors.BRIGHT_MAGENTA)
        
        await pestaña.dispatch_event("click") 
        await asyncio.sleep(1)
        
        spinner = await esperar_spinner_desaparezca(frame)
        if not spinner['success']:
            logger.log(f'⚠️ Spinner no desapareció en intento {intento + 1}', color=Colors.YELLOW)
            return {
                'success': False,
                'message': spinner['message'],
                'error_system': True
            }

        for _ in range(2):
            try:
                await frame.locator(f'//h6/b[contains(text(), "{texto_esperado}")]').wait_for(state="visible", timeout=timeout_standard)
                await asyncio.sleep(1)
                logger.log(f'✅ Pestaña {compras_o_ventas} seleccionada', color=Colors.CYAN)
                break
            except Exception as e:
                logger.log(f'⚠️ Error en intento {_+1} en esperar {tipo} seleccionarse: {e}', color=Colors.YELLOW)
                continue
        else:
            return {
                'success': False,
                'error_system': True,
                'message': f'❌ La pestaña {tipo} no cargó correctamente debido a la inestabilidad de la red',
            }

        msg = f'✅ Se seleccionó el tipo de proceso y el periodo correctamente para {compras_o_ventas} - [Año {year}] - [Mes {month}]'
        logger.log(msg, color=Colors.GREEN, force_show=True)
        return {
            'success': True,
            'message': msg,
            'error_system': False
        }

    except Exception as e:
        error_msg = f"❌ Ocurrió un error inesperado al seleccionar los periodos: {type(e).__name__} - {str(e)}"
        logger.log(error_msg, color=Colors.RED, force_show=True)
        return {
            'success': False,
            'message': error_msg,
            'error_system': True
        }

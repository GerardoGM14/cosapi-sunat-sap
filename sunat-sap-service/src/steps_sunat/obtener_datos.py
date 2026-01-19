import asyncio
from playwright.sync_api import FrameLocator, Locator
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
from src.utils.overlay import esperar_overlay_desaparezca
from src.utils.spinner import esperar_spinner_desaparezca


logger = ColoredLogger()

async def obtener_datos(frame: FrameLocator, card: str) -> IReturn:
    try:
        timeout_standard = 5000 

        card_element = frame.locator(f'//h7[@class="card-title"]//span[normalize-space(text())="{card}"]')
        await card_element.wait_for(state='visible', timeout=timeout_standard)
        
        card_text = await card_element.text_content()
        
        if not card_text:
            return {
                'success': False,
                'error_system': True,
                'message': f'❌ No se pudo obtener el texto de la tarjeta {card}',
            }

        await card_element.scroll_into_view_if_needed()

        pendientes: Locator =  frame.locator(f'//h7[.//span[normalize-space()="{card}"]]//button')
        
        await pendientes.wait_for(state='visible', timeout=timeout_standard)     

        texto_pendientes = (await pendientes.text_content()).strip()

        logger.log(f'💭 Tarjeta {card_text}. Cantidad obtenida: {texto_pendientes}', color=Colors.GREEN)
        
        if texto_pendientes == '0':
            msg = f'✅ Tarjeta {card_text} no tiene pendientes'
            logger.log(msg, color=Colors.GREEN, force_show=True)
            return {
                'success': True,
                'message': msg,
                'error_system': False
            }

        await pendientes.click()
        logger.log(f'✅ Tarjeta {card_text} clickeada', color=Colors.CYAN)

        overlay = await esperar_overlay_desaparezca(frame)
        if not overlay['success']:
            return {
                'success': False,
                'error_system': True,
                'message': overlay['message']
            }

        spinner = await esperar_spinner_desaparezca(frame)
        if not spinner['success']:
            logger.log(f'⚠️ Spinner no desapareció en intento', color=Colors.YELLOW)
            return {
                'success': False,
                'message': spinner['message'],
                'error_system': True
            }

        try:
            titleSection = frame.locator('//span[@class="m-title"]')
            await titleSection.wait_for(state='visible', timeout=timeout_standard)
            await titleSection.click(trial=True)
            logger.log(f'✅ Sección de título Gestión General apareció', color=Colors.CYAN)
            await asyncio.sleep(1)
        except Exception as e:
            return {
                'success': False,
                'error_system': True,
                'message': f'❌ Error esperando que aparezca la sección de título Gestión General: {e}',
            }

        return {
            'success': True,
            'message': '✅ Datos obtenidos',
            'error_system': False
        }
    except Exception as e:
        return {
            'success': False,
            'error_system': True,
            'message': f'❌ Error en obtener_datos: {e}',
        }

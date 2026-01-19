from playwright.async_api import Page, expect
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
import random

logger = ColoredLogger(disableModule=True)


async def login_sunat(page: Page, ruc: str, clave: str, user: str) -> IReturn:
    try:
        logger.log("🔍 Escribiendo RUC...")
        
        input_ruc = page.locator('#txtRuc')
        await input_ruc.wait_for(state='visible', timeout=5000)
        await input_ruc.highlight()
        await input_ruc.click()
        await input_ruc.press_sequentially(ruc, delay=random.uniform(30, 100))

        await page.wait_for_timeout(400)

        logger.log("🔍 Escribiendo Usuario...")
        input_usuario = page.locator('#txtUsuario')
        await input_usuario.wait_for(state='visible', timeout=5000)
        await input_usuario.click()
        await input_usuario.press_sequentially(user, delay=random.uniform(30, 100))
        await page.wait_for_timeout(400)

        logger.log("🔍 Escribiendo Clave...")
        input_clave = page.locator('//input[@id="txtContrasena"]')
        await input_clave.wait_for(state='visible', timeout=5000)
        await input_clave.click()
        await input_clave.press_sequentially(clave, delay=random.uniform(30, 100))
        await page.wait_for_timeout(400)
        
        logger.log("🔍 Click en botón Aceptar...")
        await page.locator('#btnAceptar').click()

        try:
            alert_element = page.locator('//div[@class="panel-body"]//div[@id="divMensajeError"]//div[@role="alert"]')
            await expect(alert_element).to_be_visible(timeout=2500)
            alert_text = await alert_element.text_content()
            if alert_text:
                msg = f'❌ Falla de Autenticación: {alert_text}'
                logger.log(msg, color=Colors.YELLOW, force_show=True)
                result = {
                    'success': False,
                    'message': msg,
                    'error_system': False
                }
                return result
        except Exception:
            pass

        msg = '🔐 Sesión Sunat iniciada correctamente.'
        logger.log(msg, color=Colors.GREEN, force_show=True)
        return {
            'success': True,
            'message': msg,
            'error_system': False
        }
    except Exception as e:
        msg = f'❌ Inicio sesión Sunat error: {type(e).__name__}: {e}'
        logger.log(msg, color=Colors.RED, force_show=True)
        result = {
            'success': False,
            'message': msg,
            'error_system': True
        }
        return result

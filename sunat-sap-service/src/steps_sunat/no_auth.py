from playwright.async_api import Page
from src.schemas.IReturn import IReturn


async def no_auth(page: Page) -> IReturn:
    try:
        selector = '//div[@class="container"]//div//h4/b[contains(text(), "Falla en la autenticación")]'
        
        await page.wait_for_selector(selector, timeout=3000)
        
        return {
            'success': False,
            'message': '🧱 Falla de Autenticación: No se pudo autenticar, verificar credenciales.',
            'error_system': False
        }
    except Exception:
        return {
            'success': True,
            'message': '✨ Credenciales correctas',
            'error_system': False
        }

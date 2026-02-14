from playwright.sync_api import FrameLocator
from src.schemas.IReturn import IReturn


async def esperar_spinner_desaparezca(frame: FrameLocator) -> IReturn:
    try:
        await frame.locator("//ngx-spinner/div").wait_for(state="hidden", timeout=90000)
        return {
            'success': True, 
            'message': '✅ Spinner desapareció',
            'error_system': False
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"⚠️ Timeout esperando que desaparezca spinner: {e}",
            'error_system': True
        }

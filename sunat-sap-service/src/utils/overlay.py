from playwright.sync_api import FrameLocator
from src.schemas.IReturn import IReturn



async def esperar_overlay_desaparezca(frame: FrameLocator) -> IReturn:
    try:
        await frame.locator(".black-overlay").wait_for(state="hidden", timeout=90000)
        return {
            'success': True, 
            'message': '✅ Overlay desapareció',
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"⚠️ Timeout esperando que desaparezca overlay: {str(e)}"
        }

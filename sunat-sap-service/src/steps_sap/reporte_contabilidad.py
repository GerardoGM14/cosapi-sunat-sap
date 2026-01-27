from playwright.async_api import Page
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger(disableModule=True)


async def reporte_contabilidad(page: Page) -> IReturn:
    try:
        await page.wait_for_load_state("networkidle", timeout=30000)

        encuestas_locator = page.locator('#__item1-anchorNavigationBar-1')
        await encuestas_locator.wait_for(state="visible", timeout=15000)
        await encuestas_locator.highlight()
        await encuestas_locator.click()

        await page.wait_for_timeout(3000)

        reporte_locator = page.locator(':text("Reporte Contabilidad")').last
        await reporte_locator.wait_for(state="visible", timeout=15000)
        await reporte_locator.highlight()
        await reporte_locator.click()

        iframe_selector = 'iframe[data-help-id="application-reportecontabilidad-display"], iframe[id*="__container"]'
        await page.wait_for_selector(iframe_selector, timeout=30000)
        
        frame = page.frame_locator(iframe_selector)

        section_locator = frame.locator('[id$="---Home--page-cont"]')
        await section_locator.wait_for(state="visible", timeout=30000)
        
        await frame.locator('[id$="---Home--page-title-inner"]').wait_for(state="visible", timeout=15000)
        
        await frame.locator('[id$="---Home--page-title-inner"]').inner_text()

        download_button = frame.locator('button:has-text("Descargar Excel")')
        await download_button.wait_for(state="visible", timeout=15000)
        await download_button.highlight()
        
        logger.log("✅ Página de Reporte cargada completamente dentro del iframe.", Colors.GREEN, force_show=True)

        return IReturn(
            success=True,
            message="Reporte Contabilidad cargado con éxito.",
            error_system=False,
            frame=frame
        )

    except Exception as e:
        msg = f"❌ ERROR en el flujo de Reporte Contabilidad: {e}"
        logger.log(msg, Colors.RED, force_show=True)
        await page.screenshot(path="debug_error.png", full_page=True)
        return IReturn(
            success=False,
            message=msg,
            error_system=True,
            frame=None
        )

from playwright.async_api import Page
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger(disableModule=True)


async def login_sap(page: Page, username: str, password: str) -> IReturn:
    try:
        await page.click('text=artjpgqql.accounts.ondemand.com')
        await page.wait_for_load_state("networkidle")

        username_input = page.locator('#j_username')
        await username_input.wait_for(state="visible", timeout=10000)
        await username_input.highlight()
        await username_input.click()
        await username_input.press_sequentially(username, delay=30)

        await page.wait_for_load_state("networkidle")
        password_input = page.locator('#j_password')
        await password_input.wait_for(state="visible", timeout=10000)
        await password_input.highlight()
        await password_input.click()
        await password_input.press_sequentially(password, delay=30)

        await page.locator("#logOnFormSubmit").click()

        error_selector = "#globalMessages"

        try:
            error_content = await page.locator(error_selector).text_content(timeout=5000)
            msg = f"Credenciales incorrectas o error en el login: {error_content}"
            logger.log(msg, color=Colors.YELLOW, force_show=True)
            return IReturn(
                success=False,
                message=msg,
                error_system=False
            )
        except Exception:
            await page.wait_for_load_state("networkidle")
            msg = '🔐 Sesión SAP iniciada correctamente.'
            logger.log(msg, color=Colors.GREEN, force_show=True)
            return IReturn(
                success=True,
                message="Login successful",
                error_system=False
            )

    except Exception as e:
        msg = f'❌ Inicio sesión SAP error: {type(e).__name__}: {e}'
        logger.log(msg, color=Colors.RED, force_show=True)
        return IReturn(
            success=False,
            message=msg,
            error_system=True
        )

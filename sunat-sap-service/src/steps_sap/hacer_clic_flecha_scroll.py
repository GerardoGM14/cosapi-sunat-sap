import asyncio
from playwright.async_api import Page, FrameLocator


async def hacer_clic_flecha_scroll(page: Page, frame: FrameLocator):
    vsb_selector = "div[id$='-vsb'].sapUiTableVSb"
    vsb_container = frame.locator(vsb_selector)

    async def intentar_click():
        if await vsb_container.count() > 0:
            box = await vsb_container.bounding_box()
            if box:
                await page.mouse.click(
                    box['x'] + (box['width'] / 2),
                    box['y'] + box['height'] - 8
                )
                await page.wait_for_timeout(400)
                return True
        return False

    # 🔹 Primer intento normal
    if await intentar_click():
        print("Click realizado en el scroll (primer intento).")
        await asyncio.sleep(0.5)
        return

    print("No se pudo hacer click. Haciendo scroll al body e intentando nuevamente...")

    # 🔹 Scroll al final del body (dentro del frame)
    try:
        await frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)
    except Exception as e:
        print(f"No se pudo hacer scroll al body: {e}")

    # 🔹 Segundo intento con la misma lógica original
    if await intentar_click():
        print("Click realizado en el scroll (segundo intento).")
    else:
        print("No se encontró el scroll o no está visible después del scroll.")

    await asyncio.sleep(0.5)


async def hacer_clic_flecha_scroll_(page: Page, frame: FrameLocator):
    vsb_selector = "div[id$='-vsb'].sapUiTableVSb"
    vsb_container = frame.locator(vsb_selector)
    
    if await vsb_container.count() > 0:
        box = await vsb_container.bounding_box()
        if box:
            await page.mouse.click(box['x'] + (box['width'] / 2), box['y'] + box['height'] - 8)
            await page.wait_for_timeout(400)
            
    await asyncio.sleep(2)
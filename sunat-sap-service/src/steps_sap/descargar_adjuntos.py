import os
import asyncio
from playwright.async_api import FrameLocator, Page
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
from src.steps_sap.descargara_por_fila import process_modal_downloads_one_by_one

logger = ColoredLogger()

# //div[@role="heading"]//span[contains(text(), "No se han encontrado")]


async def descargar_adjuntos(frame: FrameLocator, page: Page, folder: str) -> IReturn:
    try:
        logger.log("Iniciando descarga de adjuntos...", Colors.CYAN)

        table_selector = "div.sapUiTable" 
        await frame.locator(table_selector).first.wait_for(state="visible", timeout=10000)

        rows_selector = f"{table_selector} tr.sapUiTableRow"
        rows = frame.locator(rows_selector)
        count = await rows.count()
        logger.log(f"Filas detectadas en la tabla: {count}", Colors.BLUE)

        processed_count = 0

        for i in range(count):
            row = rows.nth(i)

            class_attr = await row.get_attribute("class")
            if "sapUiTableRowHidden" in class_attr or "sapUiTableCtrlEmpty" in class_attr:
                continue

            try:
                factura_cell = row.locator("td[data-sap-ui-colid*='column6']")
                factura_value = await factura_cell.inner_text()
                factura_value = factura_value.strip().replace("/", "-").replace("\\", "-")
            except Exception:
                factura_value = "SIN_FACTURA"

            button_visualizar = row.locator("button[title='Visualizar']")
            
            if await button_visualizar.count() == 0:
                continue

            if await button_visualizar.is_visible():

                row_folder_name = f"FILA_{i}_{factura_value}"
                row_folder_path = os.path.join(folder, row_folder_name)
                os.makedirs(row_folder_path, exist_ok=True)
                
                logger.log(f"Fila {i} [Factura: {factura_value}]: Procesando en {row_folder_path}", Colors.MAGENTA)
                
                await button_visualizar.click()

                logger.log(f"Se dio click en el boton visualizar de la fila [{i}] con factura [{factura_value}]", Colors.BRIGHT_WHITE)
                await asyncio.sleep(2)
                try:
                    no_files = frame.locator('//div[@role="heading"]//span[contains(text(), "No se han encontrado")]')
                    await no_files.wait_for(state="visible", timeout=3000)

                    if await no_files.count() > 0:
                        logger.log(f"Fila {i} [Factura: {factura_value}]: No se encontraron archivos adjuntos", Colors.YELLOW)
                        btn_close = frame.locator('//footer[@class="sapMDialogFooter"]//button')
                        await btn_close.wait_for(state="visible", timeout=3000)
                        await btn_close.click()
                        logger.log(f"Se cerró el modal de la fila [{i}] con factura [{factura_value}]\n", Colors.BRIGHT_WHITE)
                        continue
                except Exception as e:
                    logger.log(f"🤔 Modal abierto para descargar archivos adjuntos", Colors.BRIGHT_WHITE)

                modal = frame.locator("div[role='dialog'], div.sapMDialog").last 
                
                try:
                    await modal.wait_for(state="visible", timeout=2000)

                    await asyncio.sleep(2)

                    await process_modal_downloads_one_by_one(modal, page, row_folder_path)

                    await asyncio.sleep(2)

                    close_btn = modal.locator("button:has-text('Cerrar'), button:has-text('Close'), button[title='Cerrar']")
                    if await close_btn.count() > 0:
                        await close_btn.first.click()
                    else:
                        await page.keyboard.press("Escape")
                    
                    await modal.wait_for(state="hidden", timeout=5000)
                    processed_count += 1

                except Exception as e:
                    logger.log(f"Error procesando modal en fila {i+1}: {e}", Colors.RED)
                    await page.keyboard.press("Escape")

        return {
            "success": True,
            "error_system": False,
            "message": f"Fin descarga adjuntos. Filas procesadas: {processed_count}.",
            "frame": frame
        }

    except Exception as e:
        return {
            "success": False,
            "error_system": True,
            "message": f"Error en descargar_adjuntos: {e}",
            "frame": frame
        }

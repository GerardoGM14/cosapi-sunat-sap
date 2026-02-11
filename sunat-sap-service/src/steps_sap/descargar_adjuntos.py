import os
import asyncio
from playwright.async_api import FrameLocator, Page
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
from src.steps_sap.descargara_por_fila import process_modal_downloads_one_by_one
from src.steps_sap.hacer_clic_flecha_scroll import hacer_clic_flecha_scroll

logger = ColoredLogger()

    
async def descargar_adjuntos(frame: FrameLocator, page: Page, folder: str) -> IReturn:
    try:
        logger.log("Iniciando descarga de adjuntos...", Colors.CYAN)

        table_selector = "div.sapUiTable" 
        await frame.locator(table_selector).first.wait_for(state="visible", timeout=10000)

        processed_facturas = set()
        fila_real_index = 0
        # --- 1. DECLARAR VARIABLES DE CONTROL ---
        consecutive_repeats = 0
        MAX_REPEATS_LIMIT = 15

        while True:
            rows = frame.locator(f"{table_selector} tr.sapUiTableRow")
            count = await rows.count()
            
            # Si hay menos de 2 filas, no hay datos
            if count < 2:
                logger.log("No hay filas de datos suficientes.", Colors.YELLOW)
                break

            # Forzamos target_row_index = 1 para saltar siempre la cabecera (index 0)
            target_row_index = 1 
            row = rows.nth(target_row_index)

            class_attr = await row.get_attribute("class") or ""
            if "sapUiTableCtrlEmpty" in class_attr or "sapUiTableRowHidden" in class_attr:
                logger.log("Fila de datos vacía o oculta detectada.", Colors.YELLOW)
                break

            fila_real_index += 1

            if target_row_index == -1:
                break

            try:
                factura_cell = row.locator("td[data-sap-ui-colid*='column6']")
                factura_value = (await factura_cell.inner_text()).strip()
                factura_value = factura_value.replace("/", "-").replace("\\", "-")
            except:
                factura_value = "SIN_FACTURA"

            if factura_value in processed_facturas:
                # --- 2. INCREMENTAR Y VALIDAR LÍMITE ---
                consecutive_repeats += 1
                if consecutive_repeats >= MAX_REPEATS_LIMIT:
                    logger.log(f"Fin de tabla detectado: {MAX_REPEATS_LIMIT} repeticiones consecutivas.", Colors.GREEN)
                    break
                logger.log(f"Factura [{factura_value}] repetida, bajando scroll...", Colors.YELLOW)
                await hacer_clic_flecha_scroll(page, frame)
                await page.wait_for_timeout(500)
                continue
            
            # --- 3. REINICIAR CONTADOR SI LA FACTURA ES NUEVA ---
            consecutive_repeats = 0 

            processed_facturas.add(factura_value)
            button_visualizar = row.locator("button[title='Visualizar']")
            
            if await button_visualizar.is_visible():
                logger.log(f"Procesando Factura Nueva: [{factura_value}]", Colors.MAGENTA)
                await button_visualizar.click()

                await asyncio.sleep(2)

                try:
                    no_files = frame.locator('//div[@role="heading"]//span[contains(text(), "No se han encontrado")]')
                    try:
                        await no_files.wait_for(state="visible", timeout=3000)
                        if await no_files.count() > 0:
                            logger.log(f"Sin archivos adjuntos", Colors.YELLOW)
                            btn_close = frame.locator('//footer[@class="sapMDialogFooter"]//button')
                            await btn_close.click()
                    except:
                        modal = frame.locator("div[role='dialog'], div.sapMDialog").last 
                        await modal.wait_for(state="visible", timeout=2000)
                        
                        # Construimos la ruta específica para esta fila
                        row_folder_name = f"FILA_{fila_real_index}_{factura_value}"
                        row_folder_path = os.path.join(folder, row_folder_name)
                        os.makedirs(row_folder_path, exist_ok=True)

                        await process_modal_downloads_one_by_one(modal, page, row_folder_path)

                        close_btn = modal.locator("button:has-text('Cerrar'), button:has-text('Close'), button[title='Cerrar']")
                        if await close_btn.count() > 0:
                            await close_btn.first.click()
                        else:
                            await page.keyboard.press("Escape")
                        
                        await modal.wait_for(state="hidden", timeout=5000)
                except Exception as e:
                    logger.log(f"Error en modal: {e}", Colors.RED)

                logger.log("[DEBUG] Bajando scroll para siguiente fila ↓", Colors.CYAN)
                await hacer_clic_flecha_scroll(page, frame)
                await page.wait_for_timeout(500)
            else:
                await hacer_clic_flecha_scroll(page, frame)

        return {
            "success": True,
            "error_system": False,
            "message": f"Fin descarga. Procesadas: {len(processed_facturas)}",
            "frame": frame
        }

    except Exception as e:
        return {
            "success": False,
            "error_system": True,
            "message": f"Error: {e}",
            "frame": frame
        }

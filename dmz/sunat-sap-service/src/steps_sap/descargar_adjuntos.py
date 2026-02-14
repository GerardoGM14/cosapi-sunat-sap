import os
import time
import asyncio
from playwright.async_api import FrameLocator, Page
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
from src.steps_sap.descargara_por_fila import process_modal_downloads_one_by_one
from src.steps_sap.hacer_clic_flecha_scroll import hacer_clic_flecha_scroll
from src.utils.mensajes_descargas import Message

logger = ColoredLogger()


async def descargar_adjuntos(frame: FrameLocator, page: Page, folder: str) -> IReturn:
    try:
        time_init = time.time()
        
        logger.log("🚀 Iniciando descarga de adjuntos (Barrido Dinámico + Fix Ubuntu)...", Colors.CYAN)
        Message.init_process()
        
        table_selector = "div.sapUiTable" 
        await frame.locator(table_selector).first.wait_for(state="visible", timeout=10000)

        # Set para rastrear combinaciones únicas ya procesadas
        processed_rows = set()
        
        fila_real_counter = 0
        last_key = None
        consecutive_same_count = 0
        MAX_SAME_LIMIT = 20  # Reducido a 3 para detectar más rápido el fin
        no_new_data_iterations = 0
        while True:
            # 1. Obtener filas actuales en el DOM
            rows_locator = frame.locator(f"{table_selector} tr.sapUiTableRow")
            count = await rows_locator.count()
            
            new_data_processed = False

            for i in range(count):
                row = rows_locator.nth(i)
                
                # Validar si es fila vacía o de relleno
                class_attr = await row.get_attribute("class") or ""
                
                if "sapUiTableCtrlEmpty" in class_attr or "sapUiTableRowHidden" in class_attr:
                    continue

                # Extraer POSICION (Columna 2) y FACTURA (Columna 6)
                try:
                    posicion_cell = row.locator("td[data-sap-ui-colid='__column1']").first
                    posicion_value = (await posicion_cell.inner_text()).strip()
                    
                    factura_cell = row.locator("td[data-sap-ui-colid='__column6']").first
                    factura_value = (await factura_cell.inner_text()).strip()
                    
                    # Evitar procesar la cabecera
                    if not factura_value or factura_value.lower() == "factura":
                        continue
                    if not posicion_value or posicion_value.lower() in ["posicion", "position"]:
                        continue
                        
                    factura_safe = factura_value.replace("/", "-").replace("\\", "-")
                except Exception as e:
                    logger.log(f"DEBUG: Fila {i} - ERROR al extraer datos: {e}", Colors.RED)
                    continue

                # Crear clave única: POSICION + FACTURA
                row_key = f"{posicion_value}|{factura_value}"
                
                # --- DETECCIÓN DE FIN DE TABLA ---
                # Si la clave es la misma que la última procesada
                if row_key == last_key:
                    consecutive_same_count += 1
                    logger.log(f"⚠️ Misma fila detectada ({consecutive_same_count}/{MAX_SAME_LIMIT}): {posicion_value} - {factura_value}", Colors.YELLOW)
                    
                    if consecutive_same_count >= MAX_SAME_LIMIT:
                        logger.log("✅ Fin de tabla alcanzado - No hay más datos nuevos", Colors.GREEN)
                        return {
                            "success": True,
                            "error_system": False,
                            "message": f"Proceso finalizado. Total facturas procesadas: {fila_real_counter}",
                            "frame": frame
                        }
                else:
                    consecutive_same_count = 0

                # --- VERIFICAR SI YA FUE PROCESADA ---
                if row_key in processed_rows:
                    logger.log(f"   [Skip] Ya procesada: {posicion_value} - {factura_value}", Colors.YELLOW)
                    continue

                # --- NUEVA FILA DETECTADA ---
                new_data_processed = True
                fila_real_counter += 1
                processed_rows.add(row_key)
                last_key = row_key
                
                logger.log(f"-> Fila Visual [{i}] | Total [{fila_real_counter}] | Pos: {posicion_value} | Factura: {factura_value}", Colors.MAGENTA)

                # --- FIX UBUNTU: Scroll Horizontal Dinámico ---
                btn_selector = 'button[title="Visualizar"], button[title="Show"], button:has(.sapUiIcon[data-sap-ui-icon-content=""])'
                button_visualizar = row.locator(btn_selector)

                if posicion_value and int(posicion_value) != 1:
                    logger.log(f"   [Skip] Omitiendo fila con posición '{posicion_value}' (se requiere '1').", Colors.BRIGHT_RED)
                    continue

                try:
                    await button_visualizar.evaluate("node => node.scrollIntoView({ inline: 'center', block: 'nearest' })")
                    await asyncio.sleep(0.2) 
                    await button_visualizar.click()
                    await asyncio.sleep(0.2)
                    
                    try:                        
                        no_files_msg = frame.locator('//div[@role="heading"]//span[contains(text(), "No se han encontrado")]')
                        try:
                            await no_files_msg.wait_for(state="visible", timeout=3000)
                            if await no_files_msg.count() > 0:
                                logger.log(f"   Sin archivos adjuntos", Colors.YELLOW)
                                btn_close = frame.locator('//footer[@class="sapMDialogFooter"]//button')
                                await btn_close.click()
                        except:
                            modal = frame.locator("div[role='dialog'], div.sapMDialog").last 
                            await modal.wait_for(state="visible", timeout=2000)
                            
                            # CREACIÓN DE CARPETA: [FILA_REAL] [POSICION] - [FACTURA]
                            row_folder_name = f"Fila {fila_real_counter:03d} - {posicion_value} - {factura_safe}"
                            
                            Message.process_cdp(row_folder_name)
                            
                            row_folder_path = os.path.join(folder, row_folder_name)
                            os.makedirs(row_folder_path, exist_ok=True)

                            # Llamada a la función de descarga por fila
                            await process_modal_downloads_one_by_one(modal, page, row_folder_path)

                            # Cerrar modal
                            close_btn = modal.locator("button:has-text('Cerrar'), button:has-text('Close'), button[title*='Cerrar']")
                            if await close_btn.count() > 0:
                                await close_btn.first.click()
                            else:
                                await page.keyboard.press("Escape")
                            
                            await modal.wait_for(state="hidden", timeout=3000)

                    except Exception as e_modal:
                        logger.log(f"   [Aviso] No se pudo procesar modal en fila {fila_real_counter}: {e_modal}", Colors.YELLOW)
                        await page.keyboard.press("Escape")

                except Exception as e_row:
                    logger.log(f"   [Error Fila {fila_real_counter}]: {e_row}", Colors.RED)

            # --- CONTROL DE SCROLL VERTICAL ---
            if new_data_processed:
                # Se procesaron datos nuevos, resetear contador
                no_new_data_iterations = 0
                
                # Solo hacer scroll después de procesar al menos 10 filas
                if fila_real_counter >= 10:
                    logger.log(f"📜 Haciendo scroll para cargar más datos...", Colors.CYAN)
                    await hacer_clic_flecha_scroll(page, frame)
                    await page.wait_for_timeout(500)
            else:
                # No se procesó ninguna fila nueva en esta iteración
                no_new_data_iterations += 1
                logger.log(f"⚠️ Sin datos nuevos en vista ({no_new_data_iterations}/{MAX_SAME_LIMIT})", Colors.YELLOW)
                
                if no_new_data_iterations >= MAX_SAME_LIMIT:
                    logger.log("✅ Fin de tabla alcanzado - Sin datos nuevos después de múltiples iteraciones", Colors.GREEN)
                    Message.fin_process()
                    break
                
                # Intentar scroll una vez más para verificar
                if fila_real_counter >= 10:
                    logger.log(f"📜 Intentando scroll para verificar si hay más datos...", Colors.CYAN)
                    await hacer_clic_flecha_scroll(page, frame)
                    await page.wait_for_timeout(500)
                else:
                    # Si aún no llegamos a 10 filas y no hay datos nuevos, salir
                    logger.log(f"⚠️ No se ha encontrado más información en la tabla.", Colors.YELLOW)
                    break

        return {
            "success": True,
            "error_system": False,
            "message": f"Proceso finalizado. Total facturas procesadas: {fila_real_counter}",
            "frame": frame
        }

    except Exception as e:
        logger.log(f"Error General en descargar_adjuntos: {e}", Colors.RED)
        return {
            "success": False,
            "error_system": True,
            "message": f"Error General: {e}",
            "frame": frame
        }
    finally:
        Message.time_processed(time_init)

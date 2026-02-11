import os
import asyncio
from playwright.sync_api import Page, Locator
from src.logger.colored_logger import ColoredLogger, Colors

logger = ColoredLogger()


async def process_modal_downloads_one_by_one(modal: Locator, page: Page, folder: str):
    logger.log(f"\n[FOLDER] {folder}...", Colors.CYAN)
    
    list_items = modal.locator("li.sapMLIB") 
    files_count = await list_items.count()
    
    if files_count == 0:
        logger.log("\tNo se encontraron adjuntos en este modal.", Colors.YELLOW)
        return

    logger.log(f"\t> Detectados {files_count} archivos. Iniciando descarga individual...", Colors.MAGENTA)

    for j in range(files_count):
        all_checks = modal.locator("div.sapMCb input[type='CheckBox']")
        for c_idx in range(await all_checks.count()):
            cb = all_checks.nth(c_idx)
            if await cb.is_checked():
                await cb.locator("xpath=..").click()
                await asyncio.sleep(0.2)

        item = list_items.nth(j)
        
        try:
            name_el = item.locator(".sapMUCFileName, .sapMUSFileName, .sapMLnkText").first
            file_name_hint = await name_el.inner_text()
            file_name_hint = file_name_hint.strip()
        except:
            file_name_hint = f"Adjunto_{j+1}"

        logger.log(f"  [{j+1}/{files_count}] Preparando: {file_name_hint}", Colors.GREEN)

        item_cb = item.locator("div.sapMCb").first
        if await item_cb.count() > 0:
            await item_cb.click()
            await asyncio.sleep(0.3) 
        else:
            logger.log(f"  ⚠️ No se encontró checkbox para el item {j+1}", Colors.YELLOW)
            continue

        # --- PASO 3: DESCARGAR ---
        btn_descargar = modal.locator("button:has-text('Descargar Seleccionados')")
        
        if await btn_descargar.count() > 0:
            try:
                # Verificar que el botón esté habilitado
                await btn_descargar.wait_for(state="visible", timeout=5000)
                
                logger.log(f"  ⬇️ Ejecutando descarga de: {file_name_hint}", Colors.CYAN)
                
                async with page.expect_download(timeout=25000) as download_info:
                    await btn_descargar.click()
                
                await asyncio.sleep(2)

                download = await download_info.value
                save_path = os.path.join(folder, download.suggested_filename)
                await download.save_as(save_path)
                
                print(f"    - [OK] Guardado: {download.suggested_filename}")
                print(f"      Ruta: {save_path}")
                
            except Exception as e:
                logger.log(f"    - [ERROR] Error al descargar '{file_name_hint}': {e}", Colors.RED)
        else:
            logger.log(f"    - [ERROR] Botón de descarga no disponible.", Colors.RED)

        # Pausa de seguridad antes de la siguiente selección
        await asyncio.sleep(0.5)

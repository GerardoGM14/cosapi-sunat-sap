import asyncio
import os
from playwright.async_api import async_playwright
from src.logger.colored_logger import ColoredLogger, Colors
from src.schemas.IConfig import ISunat
from src.bot_manager import BotSunat
from src.schemas.IReturn import IReturn

logger = ColoredLogger()


async def appSunat(args: ISunat) -> IReturn:
    intento = 3
    for i in range(intento):
        try:
            async with async_playwright() as p:
                headless_mode = os.getenv("HEADLESS", "true").lower() == "true"
                logger.log(f"🌍 Modo Headless (SUNAT): {headless_mode}", color=Colors.CYAN)
                browser = await p.chromium.launch(headless=headless_mode)
                page = await browser.new_page()
                
                await page.goto('https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm')
                
                bot = BotSunat(
                    page=page,
                    clave=args['cred']['clave'],
                    user=args['cred']['user'],
                    ruc=args['cred']['ruc'],
                    month=args['date']['month'],
                    year=args['date']['year'],
                    folder_sunat=args['folder']
                )

                login = await bot.login_sunat()
                if not login['success']:
                    if login['error_system']:
                        continue
                    return {'success': False, 'error_system': False, 'message': login['message']}
                
                no_auth = await bot.no_auth()
                if not no_auth['success']:
                    return {'success': False, 'error_system': False, 'message': no_auth['message']}
                
                cerrar_modales_iniciales = await bot.cerrar_modales_iniciales()
                if not cerrar_modales_iniciales['success']:
                    continue
                
                entrar_al_menu_validaciones = await bot.entrar_al_menu_validaciones()
                if not entrar_al_menu_validaciones['success']:
                    continue

                await asyncio.sleep(1)
                
                seleccionar_periodos = await bot.seleccionar_periodos(frame=entrar_al_menu_validaciones['frame'])

                if not seleccionar_periodos['success']:
                    if seleccionar_periodos['error_system']:
                        continue
                    return {'success': False, 'error_system': False, 'message': seleccionar_periodos['message']}

                await asyncio.sleep(1)
                
                obtener_datos = await bot.obtener_datos(frame=entrar_al_menu_validaciones['frame'])
 
                if not obtener_datos['success']:
                    continue
                
                procesar_pendientes = await bot.procesar_pendientes(frame=entrar_al_menu_validaciones['frame'])

                if not procesar_pendientes['success']:
                    continue

                return {
                    'success': True,
                    'error_system': False,
                    'message': f"✅ Operación completada exitosamente en la iteración {i+1}"
                }

        except Exception as e:
            logger.log(f"❌ Error en la iteración {i+1}: {e}", color=Colors.BRIGHT_RED)
            continue
        finally:
            if 'browser' in locals():
                await browser.close()
    else:
        msg = f'⚠️ Después de {intento} intentos no se pudo completar la operación'
        logger.log(msg, color=Colors.YELLOW)
        return {
            'success': False,
            'error_system': False,
            'message': msg
        }

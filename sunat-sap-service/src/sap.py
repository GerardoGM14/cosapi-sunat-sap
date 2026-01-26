import asyncio
import os
from playwright.async_api import async_playwright
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
from src.schemas.IConfig import ISap
from src.bot_manager import BotSap

logger = ColoredLogger()


async def appSap(args: ISap) -> IReturn:
    intento = 3
    for i in range(intento):
        try:
            async with async_playwright() as p:
                headless_mode = os.getenv("HEADLESS", "true").lower() == "true"
                logger.log(f"🌍 Modo Headless (SAP): {headless_mode}", color=Colors.CYAN)
                browser = await p.chromium.launch(headless=headless_mode)
                page = await browser.new_page()

                await page.set_viewport_size({"width": 1600, "height": 1000})
                
                await page.goto("https://dev-f074wlvi.launchpad.cfapps.us10.hana.ondemand.com/site/portalProveedores#Shell-home")

                bot = BotSap(
                    page=page,
                    usernameSap=args['cred']['email'],
                    passwordSap=args['cred']['password'],
                    fecha=args['date'],
                    code_sociedad=args['code_sociedad'],
                    folder_sap=args['folder']
                )

                login = await bot.login_sap()
                if not login['success']:
                    if login['error_system']:
                        continue
                    return {'success': False, 'error_system': False, 'message': login['message']}

                report = await bot.reporte_contabilidad()
                if not report['success']:
                    if report['error_system']:
                        continue
                    return {'success': False, 'error_system': False, 'message': report['message']}
                
                filtro = await bot.filtro(frame=report['frame'])
                if not filtro['success']:
                    if filtro['error_system']:
                        continue
                    return {'success': False, 'error_system': False, 'message': filtro['message']}
                
                validar_filtros = await bot.validar_filtros(frame=report['frame'])
                if not validar_filtros['success']:
                    if validar_filtros['error_system']:
                        continue
                    return {'success': False, 'error_system': False, 'message': validar_filtros['message']}

                descargar_excel = await bot.descargar_excel(frame=report['frame'])
                if not descargar_excel['success']:
                    if descargar_excel['error_system']:
                        continue
                    return {'success': False, 'error_system': False, 'message': descargar_excel['message']}
                
                asyncio.sleep(3)
                
                # --- NUEVO PASO: Descargar Adjuntos ---
                print("\n" + "="*50)
                print("⏳ Iniciando descarga de adjuntos...")
                print("="*50 + "\n")

                descargar_adjuntos = await bot.descargar_adjuntos(frame=report['frame'])
                if not descargar_adjuntos['success']:
                    if descargar_adjuntos['error_system']:
                        logger.log(descargar_adjuntos['message'], color=Colors.RED)
                    else:
                        logger.log(descargar_adjuntos['message'], color=Colors.YELLOW)

                        # input("\nPresiona Enter para continuar ⏳...\n")
                    # return { ... }
                
                logger.log(descargar_adjuntos['message'], color=Colors.GREEN)
                return {
                    'success': True,
                    'error_system': False,
                    'message': descargar_excel['message'],
                    'file_path_sap': descargar_excel['file_path_sap'],
                }
        except Exception as e:
            logger.log(f"❌ Error en la iteración {i+1}: {e}", color=Colors.BRIGHT_RED)
            continue
        finally:
            await browser.close()
    else:
        msg = f'⚠️ Después de {intento} intentos no se pudo completar la operación'
        logger.log(msg, color=Colors.YELLOW)
        return {
            'success': False,
            'error_system': False,
            'message': msg
        }

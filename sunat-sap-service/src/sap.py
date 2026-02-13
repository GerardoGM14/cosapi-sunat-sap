import asyncio
from src.utils.date_current import dateCurrent
from playwright.async_api import async_playwright
from src.schemas.IReturn import IReturn
from src.logger.colored_logger import ColoredLogger, Colors
from src.schemas.IConfig import ISap
from src.bot_manager import BotSap
from src.socket_client.manager import socket_manager as io
from src.schemas.ISocket import EmitEvent
from src.config.config import Config
from src.config.config_env import ConfigEnv
from src.utils.limpiar_duplicados_excel_sap import limpiar_duplicados_excel

logger = ColoredLogger()


async def appSap(args: ISap) -> IReturn:
    intento = 3
    io.emit(
        event=EmitEvent.SAP,
        data={'message': f'🚀 Iniciando proceso de descarga de reporte contabilidad SAP', 'date': dateCurrent()}
    )
    for i in range(intento):
        try:
            async with async_playwright() as p:
                headless_mode = str(ConfigEnv.HEADLESS).lower() == 'true'
                browser = await p.chromium.launch(headless=headless_mode)
                page = await browser.new_page()

                # --- Listeners para logs del navegador ---
                page.on("console", lambda msg: logger.log(f"🌐 [CONSOLE] {msg.type}: {msg.text}", color=Colors.MAGENTA))
                page.on("pageerror", lambda err: logger.log(f"🔥 [PAGE ERROR] {err}", color=Colors.RED))
                # -----------------------------------------

                await page.set_viewport_size({"width": 1600, "height": 1000})
                
                await page.goto(Config.URL_SAP)

                async with page.context.expect_page() as new_page_info:

                    btn_start = page.locator('//button[@id="__button0"]')
                    await btn_start.wait_for(state="visible", timeout=15000)
                    await btn_start.highlight()
                    await btn_start.click()
                
                # Obtenemos la referencia a la nueva página
                new_page = await new_page_info.value
                await new_page.wait_for_load_state()
                logger.log("✅ Nueva pestaña de login capturada con éxito.", color=Colors.GREEN)

                bot = BotSap(
                    page=new_page,
                    usernameSap=args['cred']['email'],
                    passwordSap=args['cred']['password'],
                    fecha=args['date'],
                    code_sociedad=args['code_sociedad'],
                    folder_sap=args['folder']
                )

                login = await bot.login_sap()
                
                if not login['success']:
                    if login['error_system']:
                        io.emit(
                            event=EmitEvent.SAP,
                            data={'message': login['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SAP,
                        data={'message': login['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': login['message']}
                io.emit(
                    event=EmitEvent.SAP,
                    data={'message': login['message'], 'date': dateCurrent()}
                )
                
                report = await bot.reporte_contabilidad()
                
                if not report['success']:
                    if report['error_system']:
                        io.emit(
                            event=EmitEvent.SAP,
                            data={'message': report['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SAP,
                        data={'message': report['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': report['message']}
                io.emit(
                    event=EmitEvent.SAP,
                    data={'message': report['message'], 'date': dateCurrent()}
                )

                filtro = await bot.filtro(frame=report['frame'])
                if not filtro['success']:
                    if filtro['error_system']:
                        io.emit(
                            event=EmitEvent.SAP,
                            data={'message': filtro['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SAP,
                        data={'message': filtro['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': filtro['message']}
                io.emit(
                    event=EmitEvent.SAP,
                    data={'message': filtro['message'], 'date': dateCurrent()}
                )

                validar_filtros = await bot.validar_filtros(frame=report['frame'])
                
                # input(f"Presiona Enter para continuar... [Validar Filtros]: {validar_filtros}")
                
                if not validar_filtros['success']:
                    if validar_filtros['error_system']:
                        io.emit(
                            event=EmitEvent.SAP,
                            data={'message': validar_filtros['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SAP,
                        data={'message': validar_filtros['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': validar_filtros['message']}
                io.emit(
                    event=EmitEvent.SAP,
                    data={'message': validar_filtros['message'], 'date': dateCurrent()}
                )

                descargar_excel = await bot.descargar_excel(frame=report['frame'])
                if not descargar_excel['success']:
                    if descargar_excel['error_system']:
                        io.emit(
                            event=EmitEvent.SAP,
                            data={'message': descargar_excel['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SAP,
                        data={'message': descargar_excel['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': descargar_excel['message']}
                io.emit(
                    event=EmitEvent.SAP,
                    data={'message': descargar_excel['message'], 'date': dateCurrent()}
                )

                await asyncio.sleep(3)
                
                # input("Presiona Enter para continuar... [Init]")

                descargar_adjuntos = await bot.descargar_adjuntos(frame=report['frame'])
                
                # input("Presiona Enter para continuar... [Fin]")

                if not descargar_adjuntos['success']:
                    if descargar_adjuntos['error_system']:
                        io.emit(
                            event=EmitEvent.SAP,
                            data={'message': descargar_adjuntos['message'], 'date': dateCurrent()}
                        )
                        logger.log(descargar_adjuntos['message'], color=Colors.RED)
                    else:
                        io.emit(
                            event=EmitEvent.SAP,
                            data={'message': descargar_adjuntos['message'], 'date': dateCurrent()}
                        )
                        logger.log(descargar_adjuntos['message'], color=Colors.YELLOW)


                await limpiar_duplicados_excel(descargar_excel['file_path_sap'])

                io.emit(
                    event=EmitEvent.SAP,
                    data={'message': descargar_adjuntos['message'], 'date': dateCurrent()}
                )

                io.emit(
                    event=EmitEvent.SAP,
                    data={'message': '✅ Finalizando automatización SAP', 'date': dateCurrent()}
                )

                logger.log(descargar_adjuntos['message'], color=Colors.GREEN)
                return {
                    'success': True,
                    'error_system': False,
                    'message': descargar_excel['message'],
                    'file_path_sap': descargar_excel['file_path_sap'],
                }
        except Exception as e:
            msg = f"❌ Error en la iteración {i+1}: {e}"
            io.emit(
                event=EmitEvent.SAP,
                data={'message': msg, 'date': dateCurrent()}
            )
            logger.log(msg, color=Colors.BRIGHT_RED)
            await asyncio.sleep(2)
            continue
        finally:
            await browser.close()
    else:
        msg = f'⚠️ Después de {intento} intentos no se pudo completar la operación'
        io.emit(
            event=EmitEvent.SAP,
            data={'message': msg, 'date': dateCurrent()}
        )
        logger.log(msg, color=Colors.YELLOW)
        return {
            'success': False,
            'error_system': False,
            'message': msg
        }

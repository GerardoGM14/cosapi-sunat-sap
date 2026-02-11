import asyncio
from playwright.async_api import async_playwright
from src.logger.colored_logger import ColoredLogger, Colors
from src.utils.date_current import dateCurrent
from src.schemas.IConfig import ISunat
from src.bot_manager import BotSunat
from src.schemas.IReturn import IReturn
from src.socket_client.manager import socket_manager as io
from src.schemas.ISocket import EmitEvent
from src.libs.filtrar_excel_por_fecha import filtrar_excel_por_fecha
from src.config.config import Config
from src.config.config_env import ConfigEnv

logger = ColoredLogger()


async def appSunat(args: ISunat) -> IReturn:
    intento = 3
    io.emit(
        event=EmitEvent.SUNAT,
        data={'message': f'🚀 Iniciando proceso de descarga de reporte contabilidad SUNAT', 'date': dateCurrent()}
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
                
                await page.goto(Config.URL_SUNAT)
                
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
                        io.emit(
                            event=EmitEvent.SUNAT,
                            data={'message': login['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SUNAT,
                        data={'message': login['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': login['message']}
                io.emit(
                    event=EmitEvent.SUNAT,
                    data={'message': login['message'], 'date': dateCurrent()}
                )
                
                no_auth = await bot.no_auth()
                if not no_auth['success']:
                    io.emit(
                        event=EmitEvent.SUNAT,
                        data={'message': no_auth['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': no_auth['message']}
                io.emit(
                    event=EmitEvent.SUNAT,
                    data={'message': no_auth['message'], 'date': dateCurrent()}
                )
                
                cerrar_modales_iniciales = await bot.cerrar_modales_iniciales()
                if not cerrar_modales_iniciales['success']:
                    io.emit(
                        event=EmitEvent.SUNAT,
                        data={'message': cerrar_modales_iniciales['message'], 'date': dateCurrent()}
                    )
                    continue
                io.emit(
                    event=EmitEvent.SUNAT,
                    data={'message': cerrar_modales_iniciales['message'], 'date': dateCurrent()}
                )
                
                entrar_al_menu_validaciones = await bot.entrar_al_menu_validaciones()
                if not entrar_al_menu_validaciones['success']:
                    io.emit(
                        event=EmitEvent.SUNAT,
                        data={'message': entrar_al_menu_validaciones['message'], 'date': dateCurrent()}
                    )
                    continue
                io.emit(
                    event=EmitEvent.SUNAT,
                    data={'message': entrar_al_menu_validaciones['message'], 'date': dateCurrent()}
                )
                
                await asyncio.sleep(1)
                
                seleccionar_periodos = await bot.seleccionar_periodos(frame=entrar_al_menu_validaciones['frame'])

                if not seleccionar_periodos['success']:
                    if seleccionar_periodos['error_system']:
                        io.emit(
                            event=EmitEvent.SUNAT,
                            data={'message': seleccionar_periodos['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SUNAT,
                        data={'message': seleccionar_periodos['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': seleccionar_periodos['message']}
                io.emit(
                    event=EmitEvent.SUNAT,
                    data={'message': seleccionar_periodos['message'], 'date': dateCurrent()}
                )
                
                await asyncio.sleep(1)
                
                obtener_datos = await bot.obtener_datos(frame=entrar_al_menu_validaciones['frame'])
 
                if not obtener_datos['success']:
                    if obtener_datos['error_system']:
                        io.emit(
                            event=EmitEvent.SUNAT,
                            data={'message': obtener_datos['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SUNAT,
                        data={'message': obtener_datos['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': obtener_datos['message']}
                io.emit(
                    event=EmitEvent.SUNAT,
                    data={'message': obtener_datos['message'], 'date': dateCurrent()}
                )
                
                procesar_pendientes = await bot.procesar_pendientes(frame=entrar_al_menu_validaciones['frame'])

                if not procesar_pendientes['success']:
                    if procesar_pendientes['error_system']:
                        io.emit(
                            event=EmitEvent.SUNAT,
                            data={'message': procesar_pendientes['message'], 'date': dateCurrent()}
                        )
                        continue
                    io.emit(
                        event=EmitEvent.SUNAT,
                        data={'message': procesar_pendientes['message'], 'date': dateCurrent()}
                    )
                    return {'success': False, 'error_system': False, 'message': procesar_pendientes['message']}
                io.emit(
                    event=EmitEvent.SUNAT,
                    data={'message': procesar_pendientes['message'], 'date': dateCurrent()}
                )
                
                try:
                    filtrar_excel_por_fecha(
                        path_excel=procesar_pendientes['file_path_sunat'],
                        fecha_objetivo=args['input_date']
                    )
                except:
                    pass

                return {
                    'success': True,
                    'error_system': False,
                    'message': f"✅ Operación completada exitosamente en la iteración {i+1}"
                }

        except Exception as e:
            msg = f"❌ Error en la iteración {i+1}: {e}"
            io.emit(
                event=EmitEvent.SUNAT,
                data={'message': msg, 'date': dateCurrent()}
            )
            logger.log(msg, color=Colors.BRIGHT_RED)
            continue
        finally:
            await browser.close()
    else:
        msg = f'⚠️ Después de {intento} intentos no se pudo completar la operación'
        io.emit(
            event=EmitEvent.SUNAT,
            data={'message': msg, 'date': dateCurrent()}
        )
        logger.log(msg, color=Colors.YELLOW)
        return {
            'success': False,
            'error_system': False,
            'message': msg
        }

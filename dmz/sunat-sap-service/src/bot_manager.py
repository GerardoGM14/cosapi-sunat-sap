#  SAP
from src.steps_sap.login import login_sap as login_sap_step
from src.steps_sap.reporte_contabilidad import reporte_contabilidad as reporte_contabilidad_step
from src.steps_sap.validar_filtros import validar_filtros as validar_filtros_step
from src.steps_sap.filtros import filtros as filtros_step
from src.steps_sap.descargar_excel import descargar_excel as descargar_excel_step
from src.steps_sap.descargar_adjuntos import descargar_adjuntos as descargar_adjuntos_step

# SUNAT
from src.steps_sunat.login import login_sunat as login_sunat_step
from src.steps_sunat.no_auth import no_auth as no_auth_step
from src.steps_sunat.cerrar_modales_iniciales import cerrar_modales_iniciales as cerrar_modales_iniciales_step
from src.steps_sunat.entrar_al_menu_validaciones import entrar_al_menu_validaciones as entrar_al_menu_validaciones_step
from src.steps_sunat.seleccionar_periodos import seleccionar_periodos as seleccionar_periodos_step
from src.steps_sunat.obtener_datos import obtener_datos as obtener_datos_step
from src.steps_sunat.procesar_pendientes import procesar_pendientes as procesar_pendientes_step


from playwright.sync_api import FrameLocator
from playwright.async_api import Page
from src.schemas.IReturn import IReturn


class BotSap:
    def __init__(self,
        page: Page,
        usernameSap: str,
        passwordSap: str,
        fecha: str,
        code_sociedad: str,
        folder_sap: str,
    ):
        self.page = page
        self.usernameSap = usernameSap
        self.passwordSap = passwordSap
        self.fecha = fecha
        self.code_sociedad = code_sociedad
        self.folder_sap = folder_sap
    
    async def login_sap(self) -> IReturn:
        return await login_sap_step(self.page, self.usernameSap, self.passwordSap)
    
    async def reporte_contabilidad(self) -> IReturn:
        return await reporte_contabilidad_step(self.page)

    async def filtro(self, frame: FrameLocator) -> IReturn:
        return await filtros_step(fecha=self.fecha, code_sociedad=self.code_sociedad, frame=frame)
    
    async def validar_filtros(self, frame: FrameLocator) -> IReturn:
        return await validar_filtros_step(frame)

    async def descargar_excel(self, frame: FrameLocator) -> IReturn:
        return await descargar_excel_step(folder=self.folder_sap, frame=frame, page=self.page, code_sociedad=self.code_sociedad)

    async def descargar_adjuntos(self, frame: FrameLocator) -> IReturn:
        return await descargar_adjuntos_step(frame=frame, page=self.page, folder=self.folder_sap)


class BotSunat:
    def __init__(
        self,
        page: Page,
        clave: str,
        ruc: str,
        user: str,
        month: int,
        year: int,
        folder_sunat: str,
    ):
        self.page = page
        self.ruc = ruc
        self.clave = clave
        self.user = user
        self.month = month
        self.year = year
        self.folder_sunat = folder_sunat
        
    async def login_sunat(self) -> IReturn:
        return await login_sunat_step(page=self.page, clave=self.clave, ruc=self.ruc, user=self.user)

    async def no_auth(self) -> IReturn:
        return await no_auth_step(page=self.page)

    async def cerrar_modales_iniciales(self) -> IReturn:
        return await cerrar_modales_iniciales_step(page=self.page)

    async def entrar_al_menu_validaciones(self) -> IReturn:
        return await entrar_al_menu_validaciones_step(page=self.page, ruc=self.ruc, tipo_venta_compra='COMPRA')
    
    async def seleccionar_periodos(self, frame: FrameLocator) -> IReturn:
        return await seleccionar_periodos_step(ruc=self.ruc, month=self.month, year=self.year, compras_o_ventas='COMPRA', frame=frame)

    async def obtener_datos(self, frame: FrameLocator) -> IReturn:
        return await obtener_datos_step(frame=frame, card='Pendientes')

    async def procesar_pendientes(self, frame: FrameLocator) -> IReturn:
        return await procesar_pendientes_step(frame=frame, page=self.page, ruc=self.ruc, year=self.year, month=self.month, folder=self.folder_sunat, card='Pendientes')

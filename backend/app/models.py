from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, DECIMAL, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class MDataSap(Base):
    __tablename__ = "DDATA_SAP"

    iMDataSap = Column(Integer, primary_key=True, index=True) # Changed to Integer for SQLite compatibility (autoincrement)
    iMEjecucion = Column(Integer, ForeignKey("DEJECUCION.iMEjecucion"))
    tOC = Column(String(50))
    iPosicion = Column(Integer)
    tRucProveedor = Column(String(11))
    tCodigoProveedor = Column(String(50))
    tRazonSocialProveedor = Column(String)
    tSociedad = Column(String(250))
    tFactura = Column(String(50))
    fRecepcion = Column(Date)
    fEmision = Column(Date)
    tMoneda = Column(String(3))
    nImporteTotal = Column(DECIMAL(18, 3))
    tImportePagadoFecha = Column(String(50))
    nImportePendiente = Column(DECIMAL(18, 3))
    tCECO = Column(String(50))

    ejecucion = relationship("DEjecucion", back_populates="data_sap")
    descargas = relationship("MDescarga", back_populates="data_sap")

class MDataSunat(Base):
    __tablename__ = "DDATA_SUNAT"

    iMDataSunat = Column(Integer, primary_key=True, index=True)
    iMEjecucion = Column(Integer, ForeignKey("DEJECUCION.iMEjecucion"))
    tNumero = Column(String(50))
    tEmisor = Column(String)
    tAdquiriente = Column(String)
    fEmision = Column(Date)
    tFormaPago = Column(String(50))
    fDisposicion = Column(DateTime)
    tPlazoPendiente = Column(String(50))
    fPlazoAcordado = Column(Date)
    nMontoPendiente = Column(DECIMAL(18, 3))
    tMoneda = Column(String(3))
    nImporteTotal = Column(DECIMAL(18, 3))
    tMarca = Column(String(50))
    tCondicion = Column(String(50))
    tEstado = Column(String(50))
    iInconsistencias = Column(Integer)

    ejecucion = relationship("DEjecucion", back_populates="data_sunat")

class DEjecucion(Base):
    __tablename__ = "DEJECUCION"

    iMEjecucion = Column(Integer, primary_key=True, index=True)
    tTipo = Column(String(1))
    iMSAP = Column(Integer, ForeignKey("MSAP.iMSAP"))
    tRuc = Column(String(11), ForeignKey("MSOCIEDAD.tRuc"))
    fDisposicion = Column(Date)
    fEmisionDesde = Column(Date)
    fEmisionHasta = Column(Date)
    tVersionGemini = Column(String(50))
    iUsuarioEjecucion = Column(Integer, ForeignKey("MUSUARIO.iMusuario"))
    fRegistro = Column(DateTime, default=datetime.utcnow)

    msap = relationship("MSap", back_populates="ejecuciones")
    sociedad = relationship("MSociedad", back_populates="ejecuciones")
    usuario = relationship("MUsuario", back_populates="ejecuciones")
    
    data_sap = relationship("MDataSap", back_populates="ejecucion")
    data_sunat = relationship("MDataSunat", back_populates="ejecucion")
    lista_blanca_detalles = relationship("DEjecucionListaBlanca", back_populates="ejecucion")
    seguimientos = relationship("DSeguimiento", back_populates="ejecucion")
    consumos_gemini = relationship("MConsumoGemini", back_populates="ejecucion")
    descargas = relationship("MDescarga", back_populates="ejecucion")

class DEjecucionListaBlanca(Base):
    __tablename__ = "DEJECUCION_LISTA_BLANCA"

    iMDetalle = Column(Integer, primary_key=True, index=True)
    iMEjecucion = Column(Integer, ForeignKey("DEJECUCION.iMEjecucion"))
    tRucListaBlanca = Column(String(11), ForeignKey("MLISTA_BLANCA.tRucListaBlanca"))

    ejecucion = relationship("DEjecucion", back_populates="lista_blanca_detalles")
    lista_blanca = relationship("MListaBlanca", back_populates="ejecuciones_detalle")

class DSeguimiento(Base):
    __tablename__ = "DSEGUIMIENTO"

    iMSeguimiento = Column(Integer, primary_key=True, index=True)
    iMEjecucion = Column(Integer, ForeignKey("DEJECUCION.iMEjecucion"))
    iMEvento = Column(Integer, ForeignKey("MEVENTO.iMEvento"))
    fRegistro = Column(DateTime, default=datetime.utcnow)
    tDescripcion = Column(String(250))

    ejecucion = relationship("DEjecucion", back_populates="seguimientos")
    evento = relationship("MEvento", back_populates="seguimientos")

class MClaseDocumentoCompra(Base):
    __tablename__ = "MCLASE_DOCUMENTO_COMPRA"

    tClase = Column(String(5), primary_key=True) # Assuming PK based on usage, though not explicit in SQL CREATE but logical
    tDenominacion = Column(String(50))
    iRangoDesde = Column(BigInteger)
    iRangoHasta = Column(BigInteger)

class MConsumoGemini(Base):
    __tablename__ = "MCONSUMO_GEMINI"

    iMConsumo = Column(Integer, primary_key=True, index=True)
    iMEjecucion = Column(Integer, ForeignKey("DEJECUCION.iMEjecucion"))
    iTransacciones = Column(Integer)
    iTokenIn = Column(BigInteger)
    ITokenOut = Column(BigInteger)

    ejecucion = relationship("DEjecucion", back_populates="consumos_gemini")

class MDescarga(Base):
    __tablename__ = "MDESCARGA"

    iMDescarga = Column(Integer, primary_key=True, index=True)
    iMEjecucion = Column(Integer, ForeignKey("DEJECUCION.iMEjecucion"))
    iMDataSap = Column(Integer, ForeignKey("DDATA_SAP.iMDataSap"))
    tOriigen = Column(String(5))
    tRutaArchivo = Column(String)
    tExrension = Column(String(5))
    tArchivo = Column(String(100))
    tPesokb = Column(Integer)

    ejecucion = relationship("DEjecucion", back_populates="descargas")
    data_sap = relationship("MDataSap", back_populates="descargas")

class MEvento(Base):
    __tablename__ = "MEVENTO"

    iMEvento = Column(Integer, primary_key=True, index=True)
    tEvento = Column(String(50))

    seguimientos = relationship("DSeguimiento", back_populates="evento")

class MListaBlanca(Base):
    __tablename__ = "MLISTA_BLANCA"

    tRucListaBlanca = Column(String(11), primary_key=True, index=True)
    tRazonSocial = Column(String)
    lActivo = Column(Boolean, default=True)
    iUsuarioModificacion = Column(BigInteger)
    fRegistro = Column(DateTime, default=datetime.utcnow)
    iUsuarioRegistro = Column(BigInteger)
    fModificacion = Column(DateTime)

    ejecuciones_detalle = relationship("DEjecucionListaBlanca", back_populates="lista_blanca")
    sociedades = relationship("MListaBlancaSociedad", back_populates="lista_blanca", cascade="all, delete-orphan")

class MListaBlancaSociedad(Base):
    __tablename__ = "MLISTA_BLANCA_SOCIEDAD"

    iMDetalle = Column(Integer, primary_key=True, index=True)
    tRucListaBlanca = Column(String(11), ForeignKey("MLISTA_BLANCA.tRucListaBlanca"))
    tRucSociedad = Column(String(11), ForeignKey("MSOCIEDAD.tRuc"))
    
    lista_blanca = relationship("MListaBlanca", back_populates="sociedades")
    sociedad = relationship("MSociedad")

class MRol(Base):
    __tablename__ = "MROL"

    iMRol = Column(Integer, primary_key=True, index=True)
    tRol = Column(String(50))
    lActivo = Column(Boolean, default=True)

    usuarios = relationship("MUsuario", back_populates="rol")

class MSap(Base):
    __tablename__ = "MSAP"

    iMSAP = Column(Integer, primary_key=True, index=True)
    tUsuario = Column(String(100))
    tClave = Column(String(50))
    iUsuarioModificacion = Column(BigInteger)
    fRegistro = Column(DateTime, default=datetime.utcnow)
    iUsuarioRegistro = Column(BigInteger)
    fModificacion = Column(DateTime)
    lActivo = Column(Boolean, default=True)

    ejecuciones = relationship("DEjecucion", back_populates="msap")
    sap_sociedades = relationship("MSapSociedad", back_populates="msap")

class MSapSociedad(Base):
    __tablename__ = "MSAP_SOCIEDAD"

    iMDetalle = Column(Integer, primary_key=True, index=True)
    iMSAP = Column(Integer, ForeignKey("MSAP.iMSAP"))
    tRuc = Column(String(11), ForeignKey("MSOCIEDAD.tRuc"))
    lActivo = Column(Boolean, default=True)
    fRegistro = Column(DateTime, default=datetime.utcnow)
    iUsuarioRegistro = Column(BigInteger)
    fModificacion = Column(DateTime)
    iUsuarioModificacion = Column(BigInteger)

    msap = relationship("MSap", back_populates="sap_sociedades")
    sociedad = relationship("MSociedad", back_populates="sap_sociedades")

class MSociedad(Base):
    __tablename__ = "MSOCIEDAD"

    tRuc = Column(String(11), primary_key=True, index=True)
    tCodigoSap = Column(String(10)) # Codigo SAP (ej: PE01)
    tRazonSocial = Column(String(10)) # Note: SQL says nchar(10), might be short but keeping faithful
    tUsuario = Column(String(50))
    tClave = Column(String)
    iUsuarioBaja = Column(BigInteger)
    fRegistro = Column(DateTime, default=datetime.utcnow)
    iUsuarioRegistro = Column(BigInteger)
    fModificacion = Column(DateTime)
    iUsuarioModificacion = Column(BigInteger)
    fBaja = Column(DateTime)
    lActivo = Column(Boolean, default=True)

    ejecuciones = relationship("DEjecucion", back_populates="sociedad", cascade="all, delete")
    sap_sociedades = relationship("MSapSociedad", back_populates="sociedad", cascade="all, delete")

class MUsuario(Base):
    __tablename__ = "MUSUARIO"

    iMusuario = Column(Integer, primary_key=True, index=True)
    tCorreo = Column(String(250))
    tClave = Column(String)
    tNombre = Column(String(250))
    tApellidos = Column(String(250))
    iMRol = Column(Integer, ForeignKey("MROL.iMRol"))
    lNotificacion = Column(Boolean)
    fRegistro = Column(DateTime, default=datetime.utcnow)
    iUsuarioRegistro = Column(BigInteger)
    fModificacion = Column(DateTime)
    iUsuarioModificacion = Column(BigInteger)
    fBaja = Column(DateTime)
    iUsuarioBaja = Column(BigInteger)
    lActivo = Column(Boolean, default=True)
    #comentario

    rol = relationship("MRol", back_populates="usuarios")
    ejecuciones = relationship("DEjecucion", back_populates="usuario")

class MProgramacion(Base):
    __tablename__ = "MPROGRAMACION"

    iMProgramacion = Column(Integer, primary_key=True, index=True)
    tNombre = Column(String(250))
    tHora = Column(String(5)) # HH:MM
    tDias = Column(String(100)) # "Lun,Mar,Mie"
    iSociedadesCount = Column(Integer, default=0) # Cache count for list view
    lActivo = Column(Boolean, default=True)
    fRegistro = Column(DateTime, default=datetime.utcnow)
    
    sociedades = relationship("MProgramacionSociedad", back_populates="programacion", cascade="all, delete-orphan")

class MProgramacionSociedad(Base):
    __tablename__ = "MPROGRAMACION_SOCIEDAD"

    iMDetalle = Column(Integer, primary_key=True, index=True)
    iMProgramacion = Column(Integer, ForeignKey("MPROGRAMACION.iMProgramacion"))
    tRuc = Column(String(11), ForeignKey("MSOCIEDAD.tRuc"))
    
    programacion = relationship("MProgramacion", back_populates="sociedades")
    sociedad = relationship("MSociedad")

import socketio
from typing import Any
from enum import Enum

# Configuración del servidor Socket.IO
# cors_allowed_origins='*' permite conexiones desde cualquier origen
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Definición de eventos (debe coincidir con sunat-sap-service/src/schemas/ISocket.py)
class EmitEvent(str, Enum):
    SAP = 'sap:bot'
    SUNAT = 'sunat:bot'
    LOG = 'log:bot'

@sio.event
async def connect(sid, environ):
    print(f"Cliente Socket.IO conectado: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Cliente Socket.IO desconectado: {sid}")

# Manejadores de eventos
@sio.on(EmitEvent.LOG)
async def handle_log(sid, data: Any):
    # Imprimir log en consola del backend
    message = data.get('message', '') if isinstance(data, dict) else str(data)
    print(f"[BOT LOG] {message}")
    # Retransmitir a todos los clientes conectados (ej. frontend)
    await sio.emit(EmitEvent.LOG, data, skip_sid=sid)

@sio.on(EmitEvent.SAP)
async def handle_sap(sid, data: Any):
    print(f"SAP Event recibido: {data}")
    await sio.emit(EmitEvent.SAP, data, skip_sid=sid)

@sio.on(EmitEvent.SUNAT)
async def handle_sunat(sid, data: Any):
    print(f"SUNAT Event recibido: {data}")
    await sio.emit(EmitEvent.SUNAT, data, skip_sid=sid)

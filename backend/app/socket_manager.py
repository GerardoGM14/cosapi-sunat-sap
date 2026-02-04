import socketio
from typing import Any
from enum import Enum


sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

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

@sio.on(EmitEvent.LOG)
async def handle_log(sid, data: Any):
    # Mostramos el objeto completo (JSON) como pidió el usuario
    print(f"[BOT LOG] {data}")
    await sio.emit(EmitEvent.LOG, data, skip_sid=sid)

@sio.on(EmitEvent.SAP)
async def handle_sap(sid, data: Any):
    print(f"[BOT SAP] {data}")
    await sio.emit(EmitEvent.SAP, data, skip_sid=sid)

@sio.on(EmitEvent.SUNAT)
async def handle_sunat(sid, data: Any):
    print(f"[BOT SUNAT] {data}")
    await sio.emit(EmitEvent.SUNAT, data, skip_sid=sid)

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
    # Print formatted message if it's a dict with 'message'
    if isinstance(data, dict) and 'message' in data:
         print(f"[BOT LOG] {data['message']}")
    else:
         print(f"[BOT LOG] {data}")
    await sio.emit(EmitEvent.LOG, data, skip_sid=sid)

@sio.on(EmitEvent.SAP)
async def handle_sap(sid, data: Any):
    if isinstance(data, dict) and 'message' in data:
         print(f"[BOT SAP] {data['message']}")
    else:
         print(f"[BOT SAP] {data}")
    await sio.emit(EmitEvent.SAP, data, skip_sid=sid)
    # Also emit to log:bot so frontend can see it
    await sio.emit(EmitEvent.LOG, data, skip_sid=sid)

@sio.on(EmitEvent.SUNAT)
async def handle_sunat(sid, data: Any):
    if isinstance(data, dict) and 'message' in data:
         print(f"[BOT SUNAT] {data['message']}")
    else:
         print(f"[BOT SUNAT] {data}")
    await sio.emit(EmitEvent.SUNAT, data, skip_sid=sid)
    # Also emit to log:bot so frontend can see it
    await sio.emit(EmitEvent.LOG, data, skip_sid=sid)

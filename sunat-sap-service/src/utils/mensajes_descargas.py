import time
from src.utils.date_current import dateCurrent
from src.socket_client.manager import socket_manager as io
from src.schemas.ISocket import EmitEvent

    
class Message:
    @staticmethod
    def fin_process() -> None:
        io.emit(
            event=EmitEvent.SAP,
            data={
                'message': '✅ Fin de tabla alcanzado - No hay más datos nuevos',
                'date': dateCurrent()
            }
        )

    @staticmethod
    def process_cdp(row: str) -> None:
        io.emit(
            event=EmitEvent.SAP,
            data={
                'message': f"⚙️ Procesando CDP: {row}",
                'date': dateCurrent()
            }
        )

    @staticmethod
    def init_process() -> None:
        io.emit(
            event=EmitEvent.SAP,
            data={
                'message': '🚀 Iniciando procesamiento de descargas de CDPs',
                'date': dateCurrent()
            }
        )
        
    @staticmethod
    def time_processed(time_init: str) -> None:
        
        full_time = round(time.time() - time_init, 2)
        
        hh = int(full_time // 3600)
        mm = int((full_time % 3600) // 60)
        ss = int(full_time % 60)
        
        hh = str(hh).zfill(2)
        mm = str(mm).zfill(2)
        ss = str(ss).zfill(2)
        
        time_str = f"{hh}:{mm}:{ss}"
        
        io.emit(
            event=EmitEvent.SAP,
            data={
                'message': f"⏱️ Tiempo de procesamiento: {time_str}",
                'date': dateCurrent()
            }
        )

import socketio
import time
from src.logger.colored_logger import ColoredLogger, Colors
from src.schemas.ISocket import EmitEvent, IDataEmit

logger = ColoredLogger()


class SocketClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        # Use /api/socket.io to match backend configuration
        self.sio = socketio.Client(socketio_path='api/socket.io')
        self.is_connected = False
        self._register_default_events()

    def _register_default_events(self):
        @self.sio.event
        def connect():
            self.is_connected = True
            logger.log("Conectado al servidor de sockets", Colors.GREEN)

        @self.sio.event
        def disconnect():
            self.is_connected = False
            logger.log("Desconectado del servidor de sockets", Colors.YELLOW)

        @self.sio.on('*')
        def catch_all(event, data):
            # Ignore log:bot events to prevent infinite loops with the backend
            if event == 'log:bot':
                return
            logger.log(f"Evento recibido: {event}, Datos: {data}", Colors.MAGENTA)

    def connect(self):
        try:
            self.sio.connect(self.server_url)
        except socketio.exceptions.ConnectionError as e:
            logger.log(f"Error de conexión: {e}", Colors.RED)

    def disconnect(self):
        if self.is_connected:
            self.sio.disconnect()
            logger.log("Desconectado del servidor de sockets", Colors.YELLOW)

    def emit(self, event: EmitEvent, data: IDataEmit):
        if self.is_connected:
            # Importante: send_to_socket=False para evitar bucle infinito (Log -> Socket -> Log -> Socket...)
            logger.log(f"Emitiendo evento {event.value} con datos: {data}", Colors.CYAN, send_to_socket=False)
            self.sio.emit(event.value, data)
        else:
            logger.log(f"No se puede emitir el evento {event.value}, no hay conexión.", Colors.RED, send_to_socket=False)

    def on(self, event, handler=None):
        return self.sio.on(event, handler)

    def wait(self):
        try:
            if self.is_connected:
                self.sio.wait()
        except Exception as e:
            logger.log(f"Error en la espera de eventos: {e}", Colors.RED)

# if __name__ == '__main__':
#     # Ejemplo de uso
#     client = SocketClient('http://localhost:5000') # Reemplaza con la URL de tu servidor de sockets
#     client.connect()

#     if client.is_connected:
#         # Ejemplo de cómo emitir un evento
#         client.emit('paso_bot', {'paso': 'Iniciando bot de SUNAT', 'progreso': 10})
#         time.sleep(2)
#         client.emit('paso_bot', {'paso': 'Extrayendo datos de SUNAT', 'progreso': 50})
#         time.sleep(2)

#         # Ejemplo de cómo escuchar un evento personalizado
#         @client.on('respuesta_servidor')
#         def handle_respuesta(data):
#             print(f"Respuesta del servidor recibida: {data}")

#         # Mantener el cliente escuchando
#         # client.wait() # Descomenta si necesitas que el script espere por eventos

#         client.disconnect()

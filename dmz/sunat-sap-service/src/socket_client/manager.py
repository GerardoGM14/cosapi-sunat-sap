from .ioClient import SocketClient
from ..logger.colored_logger import ColoredLogger, Colors


class _SocketManager:
    def __init__(self):
        self.socket_client = None
        self.server_url = None


    def initialize(self, server_url: str):
        if not self.socket_client:
            self.server_url = server_url
            self.socket_client = SocketClient(server_url)

            ColoredLogger().log(f"Socket Manager inicializado con URL: {server_url}", color=Colors.CYAN)

    def connect(self):
        if self.socket_client and not self.socket_client.is_connected:
            self.socket_client.connect()
        elif not self.socket_client:
            ColoredLogger().log("Error: Socket Manager no inicializado. Llama a socket_manager.initialize(url) primero.", color=Colors.RED, send_to_socket=False)


    def disconnect(self):
        if self.socket_client and self.socket_client.is_connected:
            self.socket_client.disconnect()

    def emit(self, event, data):
        if self.socket_client and self.socket_client.is_connected:
            self.socket_client.emit(event, data)
        else:
            ColoredLogger().log(f"No se puede emitir evento '{event}', socket no conectado o inicializado.", color=Colors.YELLOW, send_to_socket=False)

socket_manager = _SocketManager()

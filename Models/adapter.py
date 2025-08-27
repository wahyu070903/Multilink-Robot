import socket
import threading
import json
import time
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal

@dataclass
class ClientData():
    addr: str
    data: object
    timestamp: float

class NetworkAdapterModel(QObject):
    signal_clientData = pyqtSignal(ClientData)
    signal_subscriber = pyqtSignal(dict)

    def __init__(self, host="192.168.1.4", port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        self.subscriber = []
        self.client_dataline = []
    
    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print("Server listening on", self.host, self.port)

        while self.running:
            conn, addr = server.accept()
            print("Connected:", addr)

            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()

    def handle_client(self, conn, addr):
        self.subscriber.append(conn)
        self.signal_subscriber.emit(self.subscriber)
        buffer = ""
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    msg = json.loads(line)

                    dataline = ClientData(
                        addr=str(addr),
                        data=msg,
                        timestamp=time.time()
                    )

                    self.signal_clientData.emit(dataline)

                    print("hello")
                    
                    reply = {
                                "status" : 200,
                                "message" : "success"
                            }
                    
                    reply_msg = json.dumps(reply) + "\n"
                    conn.sendall(reply_msg.encode())

                except json.JSONDecodeError:
                    print("Invalid JSON:", line)

        conn.close()
        self.subscriber.remove(conn)

import socket
import threading
import json
import time
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal

class NetworkAdapterModel(QObject):
    signal_clientData = pyqtSignal(list)
    signal_subscriber = pyqtSignal(str)

    def __init__(self, host="127.0.0.1", port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
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
        buffer = ""
        client_id = None

        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if client_id is None:
                    client_id = line.strip()
                    self.signal_subscriber.emit(client_id)
                    continue

                try:
                    msg = json.loads(line)
                    self.signal_clientData.emit([msg])

                    reply = {
                        "status": 200,
                        "message": "success"
                    }
                    conn.sendall((json.dumps(reply) + "\n").encode("utf-8"))

                except json.JSONDecodeError:
                    print("Invalid JSON:", line)

        conn.close()



import socket
import threading
import json
from PyQt5.QtCore import QObject, pyqtSignal

class NetworkAdapterModel(QObject):
    signal_clientData = pyqtSignal(list)
    signal_subscriber = pyqtSignal(str)
    signal_clientDisconnected = pyqtSignal(str)

    def __init__(self, _host="127.0.0.1", _port=700):
        super().__init__()
        self.host = _host
        self.port = _port
        self.running = True
        self.subscriber_container = []
    
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

        try:
            while True:
                data = conn.recv(1024).decode("utf-8")
                if not data:
                    self.signal_clientDisconnected.emit(client_id)
                    print("Disconnected : ", addr)
                    break

                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if client_id is None:
                        client_id = self.ListSubscriberConnection(client_id, conn)
                        if client_id:
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

        except ConnectionResetError:          
            print("disconnected : ", addr)
        
        finally:
            conn.close()

    def CheckSubscriberExistence(self, _id):
        for subs in self.subscriber_container:
            if subs["id"] is _id:
                return False
            else:
                return True

    def ListSubscriberConnection(self, _registerMsg ,_conn):
        if not _registerMsg:
            print("[Error] Empty registration message")
            return False
        
        client_id = None
        if _registerMsg.startswith("register :"):
            client_id = _registerMsg.split("register :")[1].strip()
        else:
            return False
        
        if self.CheckSubscriberExistence(client_id):
            print("[Error] Client with same Id already exist")
            return False
        
        container = {
            "id" : client_id,
            "conn" : _conn
        }
        print(container)
        self.subscriber_container.append(container)
        return client_id

    def SendDirectMessage(self, _at):
        pass


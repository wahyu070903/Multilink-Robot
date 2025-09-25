import socket
import threading
import json
import hashlib
import time
from PyQt5.QtCore import QObject, pyqtSignal

class Subscriber(QObject):
    signal_clientAdded = pyqtSignal()
    signal_clientRemoved = pyqtSignal()
    signal_clientData = pyqtSignal(int, dict)

    def __init__(self):
        super().__init__()
        self.clients = {}
    
    def CheckExistence(self, _id = None, _socket = None):
        if _id is not None and _id in self.clients:
            return True
        if _socket is not None and _socket in self.clients.values():
            return True
        return False

    def AddClients(self, _client_id, _client_socket):
        if self.CheckExistence(_client_id, _client_socket):
            return False
        
        self.clients[_client_id] = _client_socket
        self.signal_clientAdded.emit()
    
    def RemoveClients(self, _id):
        print("run disconnect func")
        if not self.CheckExistence(_id):
            return False
        del self.clients[_id]
        with open("clients.json", "r") as db:
            users = json.load(db)

        for user in users:
            if user["id"] == _id:
                user["status"] = 0
            with open("clients.json", "w") as db:
                json.dump(users, db, indent=4)
        
        self.signal_clientRemoved.emit()

    def SendControl(self, client_id, command: str):
        if client_id not in self.clients:
            print(f"[Error] Client {client_id} not found")
            return
        try:
            msg = {
                "context": "control", 
                "command": command
            }
            self.clients[client_id].sendall((json.dumps(msg) + "\n").encode("utf-8"))
            print(f"[Control] Sent to {client_id}: {command}")
        except Exception as e:
            print(f"[Error sending control to {client_id}]:", e)
    
    def SendHeartbeat(self, client_id):
        if client_id not in self.clients:
            print(f"[Error] Client {client_id} not found")
            return
        try:
            msg = {
                "context": "heartbeat", 
                "msg": "ping"
            }
            self.clients[client_id].sendall((json.dumps(msg) + "\n").encode("utf-8"))
            print(f"[Control] Sent to {client_id}: {'ping'}")
        except Exception as e:
            print(f"[Error sending control to {client_id}]:", e)

    def HandleRegistration(self, _data):
        client_id = _data["id"]
        client_signature = _data["signature"]

        with open("clients.json", "r") as db:
            users = json.load(db)

        for user in users:
            if user["id"] == client_id and user["signature"] == client_signature:
                # generate token
                timestamp = str(time.time()).encode("utf-8")
                token = hashlib.sha256(timestamp).hexdigest()
                user["token"] = token
                user["status"] = 1

                with open("clients.json", "w") as db:
                    json.dump(users, db, indent=4)
                    
                return token
        return None

    def GetClientData(self, _id):
        pass
            
class NetworkAdapterModel():
    def __init__(self, window, _host="192.168.137.1", _port=700):
        self.window = window
        self.host = _host
        self.port = _port
        self.running = True
        self.subscribers = Subscriber()
        self.lock = threading.Lock()
    
    def RunServer(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()
        print("Server listening on", self.host, self.port)
        self.window.logger.log("Server listening on " + str(self.host) + ':' + str(self.port))

        while self.running:
            conn, addr = server.accept()
            print("Connected:", addr)

            thread = threading.Thread(target=self.HandleClient, args=(conn, addr))
            thread.daemon = True
            thread.start()

    def HandleClient(self, _client_socket, _addr):
        data_buffer = ""
        client_id = None
        try:
            while True:
                request = _client_socket.recv(1024).decode("utf-8")
                data_buffer += request
                while "\n" in data_buffer:
                    line, data_buffer = data_buffer.split("\n" , 1)
                    try:
                        message = json.loads(line)
                        if message["context"] == "register":
                            client_id = message["data"]["id"]
                            token = self.subscribers.HandleRegistration(message["data"])
                            with self.lock:
                                self.subscribers.AddClients(client_id, _client_socket)
                            reply = {
                                "status" : 200,
                                "token" : token
                            }
                            _client_socket.sendall((json.dumps(reply) + "\n").encode("utf-8"))
                            self.window.logger.log('Client ' + str(client_id) + ' connected')
                            continue
                        # Receive stream data
                        if message["context"] == "stream":
                            data = message["data"]
                            print(data)
                            self.subscribers.signal_clientData.emit(client_id, data)
                            reply = {
                                "status": 200,
                                "message": "success"
                            }
                            _client_socket.sendall((json.dumps(reply) + "\n").encode("utf-8"))
                            continue

                    except json.JSONDecodeError:
                        print("[Error] Invalid JSON ", line)

                self.subscribers.SendHeartbeat(client_id)

        except Exception as err:
            print(f"[Error] Client {_addr}:", err)

        finally:
            _client_socket.close()
            if client_id:
                with self.lock:
                    self.subscribers.RemoveClients(client_id)
                print(f"Client {client_id} disconnected")
                self.window.logger.log("Client " + str(client_id) + ' disconnected')
            else:
                print("Connection to client ({}:{}) closed".format(_addr[0], _addr[1]))


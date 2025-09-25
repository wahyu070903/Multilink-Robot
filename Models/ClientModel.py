import json
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QObject, pyqtSignal

from createClientPopup import Ui_CreateClientPup
from deleteClientPopup import Ui_DeleteClientPup
from inspectClientPopup import Ui_InspectClientPup
from controlClientPopup import Ui_ClientAccessPup

class CreateClientPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_CreateClientPup()
        self.ui.setupUi(self)
        self.ui.Input_DeviceId.setValidator(QIntValidator(0, 9999))

        self.ui.Button_Create.clicked.connect(self.accept)
        self.ui.Button_Cancel.clicked.connect(self.reject)

class DeleteClientPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DeleteClientPup()
        self.ui.setupUi(self)
        self.ui.Input_Id.setValidator(QIntValidator(0, 9999))

        self.ui.Button_Delete.clicked.connect(self.accept)
        self.ui.Button_Cancel.clicked.connect(self.reject)

class InspectClientPopup(QtWidgets.QDialog):
    def __init__(self, model, adapter, parent=None):
        super().__init__(parent)
        self.ui = Ui_InspectClientPup()
        self.model = model
        self.adapter = adapter
        self.ui.setupUi(self)
        self.ui.Input_Id.setValidator(QIntValidator(0, 9999))
        self.valid_devid = None
        self.adapter.subscribers.signal_clientData.connect(self.OnClientData)
        self.startConnection = False

        self.ui.check_btn.clicked.connect(self.CheckClient)
        self.ui.connect_btn.clicked.connect(self.ConnectClient)


    def CheckClient(self):
        devid = self.ui.Input_Id.text().strip()
        if devid:
            devid = int(devid)

        user = self.model.GetClient(devid)
        if user:
            client_status = user["status"]
            if client_status == 1:
                self.ui.lamp.setStyleSheet("background-color: green; border-radius: 10px;")
                self.valid_devid = devid
            elif client_status == 0:
                self.ui.lamp.setStyleSheet("background-color: red; border-radius: 10px;")
                self.valid_devid = None
        else:
            self.ui.lamp.setStyleSheet("background-color: gray; border-radius: 10px;")
            self.valid_devid = None
            return False
    
        return self.valid_devid

    def ConnectClient(self):
        if self.valid_devid:
            self.startConnection = True
        else:
            self.startConnection = False
    
    def UpdateClientData(self, data):
        self.ui.devid_value.setText(str(self.valid_devid))
        self.ui.status_value.setText(str(data["status"]))
        
        ultrasonic_data = data["ultrasonic"]
        self.ui.ultrasonic_left_value.setText(str(ultrasonic_data["l"]))
        self.ui.ultrasonic_mid_value.setText(str(ultrasonic_data["m"]))
        self.ui.ultrasonic_right_value.setText(str(ultrasonic_data["r"]))

        motor_data = data["motor"]
        self.ui.motor_speed_value.setText(str(motor_data["speed"]))
        self.ui.motor_status_value.setText(str(motor_data["status"]))

        accel_data = data["imu"]["accel"]
        self.ui.acc_ax_value.setText(str(accel_data["ax"]))
        self.ui.acc_ay_value.setText(str(accel_data["ay"]))
        self.ui.acc_az_value.setText(str(accel_data["az"]))

        gyro_data = data["imu"]["gyro"]
        self.ui.gyro_ax_value.setText(str(gyro_data["ax"]))
        self.ui.gyro_ay_value.setText(str(gyro_data["ay"]))
        self.ui.gyro_az_value.setText(str(gyro_data["az"]))

        derived_data = data["imu"]["derived"]
        self.ui.pitch_value.setText(str(derived_data["pitch"]))
        self.ui.roll_value.setText(str(derived_data["roll"]))


    def OnClientData(self, client_id, client_data):
        if self.valid_devid == client_id and self.startConnection:
            self.UpdateClientData(client_data)

class ClientAccessPopup(QtWidgets.QDialog):
    def __init__(self, model, adapter, parent=None):
        super().__init__(parent)
        self.model = model
        self.adapter = adapter
        self.ui = Ui_ClientAccessPup()
        self.ui.setupUi(self)
        self.ui.devid.setValidator(QIntValidator(0, 9999))
        self.start_connection = False
        self.devid = None
        self.ui.button_up.clicked.connect(lambda: self.CommandUp())
        self.ui.button_down.clicked.connect(lambda: self.CommandDowm())
        self.ui.button_right.clicked.connect(lambda: self.CommandRight())
        self.ui.button_left.clicked.connect(lambda: self.CommandLeft())
        self.ui.button_takeover.clicked.connect(lambda: self.TakeOver())
    
    def CheckClient(self):
        self.devid = self.ui.devid.text().strip()
        if self.devid:
            self.devid = int(self.devid)

        user = self.model.GetClient(self.devid)
        if user:
            return True
        return False
    
    def TakeOver(self):
        if self.CheckClient():
            self.start_connection = True
            self.ui.lamp.setStyleSheet("background-color: green; border-radius: 10px;")
        else:
            self.start_connection = False
            return False
    
    def CommandUp(self):
        self.adapter.subscribers.SendControl(self.devid, "command:up")
    def CommandDowm(self):
        self.adapter.subscribers.SendControl(self.devid, "command:down")
    def CommandRight(self):
        self.adapter.subscribers.SendControl(self.devid, "command:right")
    def CommandLeft(self):
        self.adapter.subscribers.SendControl(self.devid, "command:left")

class ClientModel(QObject):
    signal_clientUpdate = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.dbname = "clients.json"
    
    def CreateClient(self):
        widget_create = CreateClientPopup()
        result = widget_create.exec_()

        if result == QtWidgets.QDialog.Accepted:
            device_id = int(widget_create.ui.Input_DeviceId.text().strip())
            signature = widget_create.ui.lineEdit_2.text().strip()
        else:
            return False
    
        with open(self.dbname, "r") as db:
            users = json.load(db)

        for user in users:
            if user["id"] == device_id:
                QtWidgets.QMessageBox.warning(
                    None,
                    "Error",
                    f"Device ID {device_id} already exists!"
                )
                return False

        new_client = {
            "id" : device_id,
            "signature" : signature,
            "token" : "",
            "status" : 0
        }
        users.append(new_client)

        with open(self.dbname, "w") as db:
            json.dump(users, db, indent=4)

        QtWidgets.QMessageBox.information(
            None,
            "Success",
            f"Client with ID {device_id} created successfully!"
        )
        self.signal_clientUpdate.emit()
        return True
    
    def DeleteClient(self):
        widget_create = DeleteClientPopup()
        result = widget_create.exec_()

        if result == QtWidgets.QDialog.Accepted:
            device_id = int(widget_create.ui.Input_Id.text().strip())
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Confirm Delete")
            msg.setText("Are you sure you want to delete this client?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Cancel)

            msg_result = msg.exec_()
            if msg_result == QMessageBox.Ok:
                with open(self.dbname, "r") as db:
                    users = json.load(db)

                users = [user for user in users if user["id"] != device_id]

                with open(self.dbname, "w") as db:
                    json.dump(users, db, indent=4)

                self.signal_clientUpdate.emit()
                return True
            else:
                return False
        else:
            return False
    
    def GetClient(self, _id):
        with open(self.dbname, "r") as db:
            users = json.load(db)
        
        for user in users:
            if user["id"] == _id:
                return user
            
        return False
    
    def InspectClient(self, adapter):
        widget_create = InspectClientPopup(self, adapter)
        widget_create.exec_()

    def TakeoverClient(self, adapter):
        widget_create = ClientAccessPopup(self, adapter)
        widget_create.exec_()
        
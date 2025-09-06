from PyQt5.QtWidgets import QFrame, QDialog
from robotNodeFrame import Ui_RobotNode
from PyQt5.QtCore import Qt
from manualControlDialog import Ui_ManControl

class ControlPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_ManControl()
        self.ui.setupUi(self) 

class RobotNodeModel():
    def __init__(self, window, _subscriberModel):
        self.window = window
        self.subsriberModel = _subscriberModel
        self.frames = {}
        self.subsscriber = []
        self.control_popup = None

    def RenderNodes(self):
        current_ids = {item["id"] for item in self.subsscriber}

        for node_id in list(self.frames.keys()):
            if node_id not in current_ids:
                frame_ui = self.frames.pop(node_id)
                frame_ui.frame.setParent(None)

        for i, item in enumerate(self.subsscriber):
            node_id = item["id"]

            if node_id not in self.frames:
                frame = QFrame()
                frame_ui = Ui_RobotNode()
                frame_ui.setupUi(frame)

                frame_ui.frame = frame
                self.frames[node_id] = frame_ui

                self.window.ui.gridLayout.addWidget(frame, i, 0, alignment=Qt.AlignTop | Qt.AlignLeft)

                frame_ui.ControlMode.clicked.connect(self.open_control_popup)
            else:
                frame_ui = self.frames[node_id]

            frame_ui.label_id.setText(str(item["id"]))
            frame_ui.label_cmode.setText(item["data"]["control-mode"])
            frame_ui.label_status.setText(item["data"]["status"])

            frame_ui.label_accel_ax.setText(str(item["data"]["imu"]["accel"]["ax"]))
            frame_ui.label_accel_ay.setText(str(item["data"]["imu"]["accel"]["ay"]))
            frame_ui.label_accel_az.setText(str(item["data"]["imu"]["accel"]["az"]))

    def open_control_popup(self):
        self.control_popup = ControlPopup()
        self.control_popup.exec_() 

    def close_control_popup(self):
        self.control_popup.close()
        self.control_popup = None

    def UpdateData(self):
        self.subsscriber = self.subsriberModel.GetSubscribers()
        self.RenderNodes()

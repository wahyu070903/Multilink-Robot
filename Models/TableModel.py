from PyQt5.QtWidgets import QTableWidgetItem, QVBoxLayout
from Models.SubscriberModel import SubscriberModel

class RobotTableModel():
    def __init__(self, window, _subscriberModel):
        self.window = window
        self.window.ui.NodeTable.setColumnCount(6)
        self.window.ui.NodeTable.setRowCount(5)
        self.window.ui.NodeTable.setHorizontalHeaderLabels([
            "ID",
            "Control Mode",
            "State",
            "Target Relative X [m]",
            "Target Relative Y [m]",
            "Target Relative Z [m]",
        ])

        self.subscriber_model = _subscriberModel
        self.subscriber = []
        self.last_update = None
        self.RenderData()

    def RenderData(self):
        self.window.ui.NodeTable.clearContents()
        for row, item in enumerate(self.subscriber):
            data = item["data"]
            self.window.ui.NodeTable.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.window.ui.NodeTable.setItem(row, 1, QTableWidgetItem(data["control-mode"]))
            self.window.ui.NodeTable.setItem(row, 2, QTableWidgetItem(data["status"]))
            self.window.ui.NodeTable.setItem(row, 3, QTableWidgetItem(str(data["imu"]["accel"]["ax"])))
            self.window.ui.NodeTable.setItem(row, 4, QTableWidgetItem(str(data["imu"]["accel"]["ay"])))
            self.window.ui.NodeTable.setItem(row, 5, QTableWidgetItem(str(data["imu"]["accel"]["az"])))

    def UpdateData(self):
        self.subscriber = self.subscriber_model.GetSubscribers()
        self.RenderData()
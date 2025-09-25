import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QHeaderView
from Models.SubscriberModel import SubscriberModel
from PyQt5.QtGui import QIcon

class RobotTableModel():
    def __init__(self, window):
        self.window = window
        self.window.ui.NodeTable.setColumnCount(5)
        header =  self.window.ui.NodeTable.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.window.ui.NodeTable.setColumnWidth(0, 50)

        header.setSectionResizeMode(1, QHeaderView.Fixed)
        self.window.ui.NodeTable.setColumnWidth(1, 100)

        for col in range(2, self.window.ui.NodeTable.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        self.window.ui.NodeTable.setHorizontalHeaderLabels([
            "ID",
            "State",
            "Target Relative X [m]",
            "Target Relative Y [m]",
            "Target Relative Z [m]",
        ])

        self.users = []
        self.subscriber = []
        self.last_update = None
        self.ReadDatabase()
        self.RenderData()

    def RenderData(self):
        self.window.ui.NodeTable.clearContents()
        user_len = len(self.users)
        self.window.ui.NodeTable.setRowCount(user_len)
        for row, user in enumerate(self.users):
            item_id = QTableWidgetItem(str(user["id"]))
            item_id.setTextAlignment(Qt.AlignCenter)
            
            # delete_btn = QPushButton("Delete")
            # view_btn = QPushButton("View")
            # delete_btn.clicked.connect(lambda: self.window.clientModel.DeleteClient(int(user["id"])))

            # widget_btn = QWidget()
            # widget_btn.setContentsMargins(0, 0, 0, 0)
            # layout = QHBoxLayout()
            # layout.addWidget(delete_btn)
            # layout.addWidget(view_btn)
            # layout.setContentsMargins(0, 0, 0, 0)
            # widget_btn.setLayout(layout)
            
            user_status = user["status"]
            if user_status == 1:
                user_status = "Online"
                item_status = QTableWidgetItem(str(user_status))
                item_status.setIcon(QIcon("icons/green-dot.png"))
            else:
                user_status = "Offline"
                item_status = QTableWidgetItem(str(user_status))
                item_status.setIcon(QIcon("icons/red-dot.png"))

            self.window.ui.NodeTable.setItem(row, 0, item_id)
            self.window.ui.NodeTable.setItem(row, 1, item_status)
            # self.window.ui.NodeTable.setCellWidget(row, 5, widget_btn)

        # for row, item in enumerate(self.subscriber):
        #     data = item["data"]
        #     self.window.ui.NodeTable.setItem(row, 0, QTableWidgetItem(str(item["id"])))
        #     self.window.ui.NodeTable.setItem(row, 1, QTableWidgetItem(data["control-mode"]))
        #     self.window.ui.NodeTable.setItem(row, 2, QTableWidgetItem(data["status"]))
        #     self.window.ui.NodeTable.setItem(row, 3, QTableWidgetItem(str(data["imu"]["accel"]["ax"])))
        #     self.window.ui.NodeTable.setItem(row, 4, QTableWidgetItem(str(data["imu"]["accel"]["ay"])))
        #     self.window.ui.NodeTable.setItem(row, 5, QTableWidgetItem(str(data["imu"]["accel"]["az"])))

    def ReadDatabase(self):
        with open("clients.json", "r") as database:
            users = json.load(database)
        self.users = users
        self.RenderData()
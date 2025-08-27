from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QTimer, QRectF, Qt
from PyQt5.QtGui import QBrush
from mainScreen import Ui_MainWindow

import sys
import random
import threading
import json
from Models.adapter import NetworkAdapterModel

class SwarmSimulation(QGraphicsView):
    def __init__(self, num_robots=10, width=600, height=400):
        super().__init__()
        self.num_robots = num_robots
        self.width = width
        self.height = height

        # Setup scene
        self.scene = QGraphicsScene(0, 0, width, height)
        self.setScene(self.scene)

        self.robots = []
        for _ in range(num_robots):
            x, y = random.randint(0, width), random.randint(0, height)
            robot = QGraphicsEllipseItem(QRectF(0, 0, 10, 10))
            robot.setPos(x, y)
            robot.setBrush(QBrush(Qt.blue))
            self.scene.addItem(robot)
            self.robots.append(robot)

        # Timer untuk update posisi
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(200)  # update setiap 200ms

    def update_positions(self):
        for robot in self.robots:
            # Random movement sederhana
            dx, dy = random.randint(-10, 10), random.randint(-10, 10)
            new_x = min(max(robot.x() + dx, 0), self.width)
            new_y = min(max(robot.y() + dy, 0), self.height)
            robot.setPos(new_x, new_y)


class RobotNodeTable():
    def __init__(self, window, datas):
        super().__init__()
        window.ui.NodeTable.setColumnCount(6)
        window.ui.NodeTable.setRowCount(5)

        window.ui.NodeTable.setHorizontalHeaderLabels([
            "ID",
            "Control Mode",
            "State",
            "Target Relative X [m]",
            "Target Relative Y [m]",
            "Target Relative Z [m]",
        ])
        
        table_data = []
        
        for data in datas:
            data_construct = data
            data_construct["x"] = 200   
            data_construct["y"] = 200
            data_construct["z"] = 200  
            table_data.append(data_construct)
        
        for row, item in enumerate(table_data):
            window.ui.NodeTable.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            window.ui.NodeTable.setItem(row, 1, QTableWidgetItem(item["control-mode"]))
            window.ui.NodeTable.setItem(row, 2, QTableWidgetItem(item["status"]))
            window.ui.NodeTable.setItem(row, 3, QTableWidgetItem(str(item["x"])))
            window.ui.NodeTable.setItem(row, 4, QTableWidgetItem(str(item["y"])))
            window.ui.NodeTable.setItem(row, 5, QTableWidgetItem(str(item["z"])))
        
        layout = QVBoxLayout()
        layout.addWidget(window.ui.NodeTable)
        window.setLayout(layout)

    def update_tableData(self, data):
        self.config_data.robots = data
        # Update the UI table with the new data
        RobotNodeTable(self, self.config_data.robots)

class window(QtWidgets.QMainWindow):
    def __init__(self):
        super(window, self) .__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.config_data = configAdapter()

        RobotNodeTable(self, self.config_data.robots)
        self.sim = SwarmSimulation()
        self.ui.SwarmView.setScene(self.sim.scene)

        self.ui.AddNodeButton.clicked.connect(lambda: self.config_data.addRobotNode())

        self.net_thread = NetworkAdapterModel()

        self.net_thread.signal_clientData.connect(self.update_tableData)

        thread = threading.Thread(target=self.net_thread.run, daemon=True)
        thread.start()


class configAdapter:
    def __init__(self, filename="config.json"):
        self.name = "config"
        self.filename = filename
        self.config_data = None
        self.robots = None
        
        with open(self.filename, "r") as config:
            self.config_data = json.load(config)

        if self.config_data:
            self.robots = self.config_data.get("robots", [])

    def addRobotNode(self, new_robot=None):
        if new_robot is None:
            new_robot = {"id": 69, "control-mode": "auto", "status": "active"}

        if self.config_data:
            self.robots.append(new_robot)
            with open(self.filename, "w") as config:
                json.dump(self.config_data, config, indent=4)


def create_app():
    app = QtWidgets.QApplication(sys.argv)
    win = window()
    win.show()
    
    sys.exit(app.exec())

create_app()
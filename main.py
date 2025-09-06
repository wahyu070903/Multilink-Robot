from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import QTimer, QRectF, Qt
from PyQt5.QtGui import QBrush
from mainScreen import Ui_MainWindow

import sys
import random
import threading
import json
from Models.AdapterModel import NetworkAdapterModel
# from Models.TableModel import RobotTableModel
# from Models.RobotNodeModel import RobotNodeModel
# from Models.SubscriberModel import SubscriberModel

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

class window(QtWidgets.QMainWindow):
    def __init__(self):
        super(window, self) .__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.config_data = configAdapter()
        # self.subscriber_model = SubscriberModel()

        # construct data table and initialize   
        # self.robot_table = RobotTableModel(self, self.subscriber_model)
        # self.robot_table.changeAllValue(self.config_data.robots)
        
        # self.robot_node = RobotNodeModel(self, self.subscriber_model)

        self.sim = SwarmSimulation()
        self.ui.SwarmView.setScene(self.sim.scene)

        self.ui.AddNodeButton.clicked.connect(lambda: self.config_data.addRobotNode())

        self.net_thread = NetworkAdapterModel()

        # self.net_thread.signal_subscriber.connect(self.subscriber_model.ListAllSubscriber)
        # self.net_thread.signal_clientData.connect(self.subscriber_model.UpdateSubscriberValues)
        # self.net_thread.signal_clientDisconnected.connect(self.subscriber_model.HandleCLientDisconnection)

        # self.subscriber_model.signal_updateping.connect(self.robot_table.UpdateData)
        # self.subscriber_model.signal_updateping.connect(self.robot_node.UpdateData)

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
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import QTimer, QRectF, Qt, QObject, pyqtSignal
from PyQt5.QtGui import QBrush, QTextCursor, QColor
from mainScreen import Ui_MainWindow

import sys
import random
import threading
import json
from datetime import datetime
from Models.AdapterModel import NetworkAdapterModel
from Models.TableModel import RobotTableModel
from Models.ClientModel import ClientModel
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

class TerminalLogger(QObject):
    log_signal = pyqtSignal(str, str)  # (message, color)

    def __init__(self, text_edit: QTextEdit, max_lines=100):
        super().__init__()
        self.text_edit = text_edit
        self.max_lines = max_lines
        self.buffer = []

        self.text_edit.setReadOnly(True)
        self.log_signal.connect(self._append_log)

    def log(self, message, color="black"):
        self.log_signal.emit(message, color)

    def _append_log(self, message, color):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        line = f"{timestamp} => {message}"

        self.buffer.append((line, color))
        if len(self.buffer) > self.max_lines:
            self.buffer.pop(0)

        self.text_edit.clear()
        for l, c in self.buffer:
            self.text_edit.setTextColor(QColor(c))
            self.text_edit.append(l)

        self.text_edit.moveCursor(QTextCursor.End)

class window(QtWidgets.QMainWindow):
    def __init__(self):
        super(window, self) .__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        

        self.sim = SwarmSimulation()
        self.ui.SwarmView.setScene(self.sim.scene)

        self.logger = TerminalLogger(self.ui.TerminalDisplay, max_lines=100)
        
        self.clientModel = ClientModel()

        self.ui.AddNodeButton.clicked.connect(lambda: self.clientModel.CreateClient())
        self.ui.DelNodeButton.clicked.connect(lambda: self.clientModel.DeleteClient())
        self.ui.InspectButton.clicked.connect(lambda: self.clientModel.InspectClient(self.net_thread))
        self.ui.AccessButton.clicked.connect(lambda: self.clientModel.TakeoverClient(self.net_thread))

        self.net_thread = NetworkAdapterModel(self)
        self.robot_table = RobotTableModel(self)
        self.net_thread.subscribers.signal_clientAdded.connect(self.robot_table.ReadDatabase)
        self.net_thread.subscribers.signal_clientRemoved.connect(self.robot_table.ReadDatabase)
        self.clientModel.signal_clientUpdate.connect(self.robot_table.ReadDatabase)
    
        thread = threading.Thread(target=self.net_thread.RunServer, daemon=True)
        thread.start()
        

def create_app():
    app = QtWidgets.QApplication(sys.argv)
    win = window()
    win.show()
    
    sys.exit(app.exec())

create_app()
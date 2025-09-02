from PyQt5.QtWidgets import QTableWidgetItem, QVBoxLayout, QFrame
from robotNodeFrame import Ui_RobotNode

class RobotNodeModel():
    def __init__(self, window):
        self.window = window
        
        frame1 = QFrame()                       
        self.frame1_ui = Ui_RobotNode()        
        self.frame1_ui.setupUi(frame1)   

        frame2 = QFrame()
        self.frame2_ui = Ui_RobotNode()
        self.frame2_ui.setupUi(frame2)

        self.window.ui.gridLayout.addWidget(frame1, 0, 0)
        self.window.ui.gridLayout.addWidget(frame2, 0, 1)

    def renderNodes(self, data):
        pass
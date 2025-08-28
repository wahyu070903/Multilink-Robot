from PyQt5.QtWidgets import QTableWidgetItem, QVBoxLayout

class RobotTableModel():
    def __init__(self, window):
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
        
        self.inner_data = []
        self.inner_data_complete = []
        self.allnode_data = []
        self.subscriber = []

        self.renderData()

    def renderData(self):
        self.window.ui.NodeTable.clearContents()
        # for data in self.inner_data:
        #     data_construct = data
        #     data_construct["x"] = data["ax"]   
        #     data_construct["y"] = data["ay"]
        #     data_construct["z"] = data["az"]
        #     self.inner_data_complete.append(data_construct)
        print(self.subscriber)
        for row, item in enumerate(self.subscriber):
            data = item["data"]
            self.window.ui.NodeTable.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.window.ui.NodeTable.setItem(row, 1, QTableWidgetItem(data["control-mode"]))
            self.window.ui.NodeTable.setItem(row, 2, QTableWidgetItem(data["status"]))
            self.window.ui.NodeTable.setItem(row, 3, QTableWidgetItem(str(data["ax"])))
            self.window.ui.NodeTable.setItem(row, 4, QTableWidgetItem(str(data["ay"])))
            self.window.ui.NodeTable.setItem(row, 5, QTableWidgetItem(str(data["az"])))

        self.inner_data_complete.clear()
        self.inner_data.clear()

    def changeSubscriberValue(self, new_data):
        data = new_data[0]
        target_id = new_data[0].get("id", None)
        for container in self.subscriber:
            if int(container["id"]) == target_id:
                container["data"]["control-mode"] = data["control-mode"]
                container["data"]["status"] = data["status"]
                container["data"]["ax"] = data["ax"]
                container["data"]["ay"] = data["ay"]
                container["data"]["az"] = data["az"]

                self.renderData()
                return True

        print("[Error] Target ID not found:", target_id)
        return False


    def listAllSubscriber(self, subscriber):
        new_datacontainer = {
            "id" : subscriber,
            "data" : {
                "control-mode" : "None",
                "status" : "None",
                "ax" : None,
                "ay" : None,
                "az" : None
            }
        }

        self.subscriber.append(new_datacontainer)
        print(self.subscriber)
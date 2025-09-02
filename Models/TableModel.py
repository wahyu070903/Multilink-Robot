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
        self.subscriber = []

        self.renderData()

    def renderData(self):
        self.window.ui.NodeTable.clearContents()
        for row, item in enumerate(self.subscriber):
            data = item["data"]
            self.window.ui.NodeTable.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.window.ui.NodeTable.setItem(row, 1, QTableWidgetItem(data["control-mode"]))
            self.window.ui.NodeTable.setItem(row, 2, QTableWidgetItem(data["status"]))
            self.window.ui.NodeTable.setItem(row, 3, QTableWidgetItem(str(data["imu"]["accel"]["ax"])))
            self.window.ui.NodeTable.setItem(row, 4, QTableWidgetItem(str(data["imu"]["accel"]["ay"])))
            self.window.ui.NodeTable.setItem(row, 5, QTableWidgetItem(str(data["imu"]["accel"]["az"])))

        self.inner_data_complete.clear()
        self.inner_data.clear()

    def changeSubscriberValue(self, new_data):
        data = new_data[0]
        target_id = new_data[0].get("id", None)
        for container in self.subscriber:
            if int(container["id"]) == target_id:
                container["data"]["control-mode"] = data["control-mode"]
                container["data"]["status"] = data["status"]
                
                ultrasonic_data = container["data"]["ultrasonic"]
                ultrasonic_data["l"] = data["ultrasonic"]["l"]
                ultrasonic_data["m"] = data["ultrasonic"]["m"]
                ultrasonic_data["r"] = data["ultrasonic"]["r"]  

                motor_data = container["data"]["motor"]
                motor_data["status"] = data["motor"]["status"]
                motor_data["speed"] = data["motor"]["speed"]

                imu_data_accel = container["data"]["imu"]["accel"]
                imu_data_accel["ax"] = data["imu"]["accel"]["ax"]
                imu_data_accel["ay"] = data["imu"]["accel"]["ay"]
                imu_data_accel["az"] = data["imu"]["accel"]["az"]

                imu_data_gyro = container["data"]["imu"]["gyro"]
                imu_data_gyro["ax"] = data["imu"]["gyro"]["ax"]
                imu_data_gyro["ay"] = data["imu"]["gyro"]["ay"]
                imu_data_gyro["az"] = data["imu"]["gyro"]["az"]

                imu_data_deriv = container["data"]["imu"]["derived"]
                imu_data_deriv["pitch"] = data["imu"]["derived"]["pitch"]
                imu_data_deriv["roll"] = data["imu"]["derived"]["roll"]

                self.renderData()
                return True

        print("[Error] Target ID not found:", target_id)
        return False

    def IsSubscriberExist(self, subscriber_id):
        return any(item["id"] == subscriber_id for item in self.subscriber)

    def HandleCLientDisconnection(self, subscriber):
        print("sub : ", subscriber)
        for item in self.subscriber:
            if item["id"] == subscriber:
                self.subscriber.remove(item)
                self.renderData()
                return True 
        
        return False 
        
    def listAllSubscriber(self, subscriber):
        if self.IsSubscriberExist(subscriber):
            return 0        # Skip when subscriber already in container
        
        new_datacontainer = {
            "id" : subscriber,
            "data" : {
                "control-mode" : "None",
                "status" : "None",
                "ultrasonic" : {
                    "l" : None,
                    "m" : None,
                    "r" : None,
                },
                "motor" : {
                    "status" : None,
                    "speed" : None,
                },
                "imu" : {
                    "accel" : {
                        "ax" : None,
                        "ay" : None,
                        "az" : None,
                    },
                    "gyro" : {
                        "ax" : None,
                        "ay" : None,
                        "az" : None,
                    },
                    "derived" : {
                        "pitch" : None,
                        "roll" : None,
                    }
                }
            }
        }

        self.subscriber.append(new_datacontainer)
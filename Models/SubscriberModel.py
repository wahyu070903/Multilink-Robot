

class SubscriberModel:
    def __init__(self):
        self.subscriber = []

    def IsSubscriberExist(self, subscriber_id):
        return any(item["id"] == subscriber_id for item in self.subscriber)
    
    def ListAllSubscriber(self, _subscriber):
        if self.IsSubscriberExist(_subscriber):
            # Skip when subscriber already in container
            return 0
        
        new_datacontainer = {
            "id" : _subscriber,
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

    def UpdateSubscriberValues(self, _new_data):
        data = _new_data[0]
        target_id = _new_data[0].get("id", None)
        for container in self.subscriber:
            if int(container["id"]) == target_id:
                print(container)
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
    
    def HandleCLientDisconnection(self, subscriber):
        print("sub : ", subscriber)
        for item in self.subscriber:
            if item["id"] == subscriber:
                self.subscriber.remove(item)
                self.renderData()
                return True 
        
        return False 
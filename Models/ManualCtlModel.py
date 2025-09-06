class ManualCtlModel():
    def __init__(self, window, _client_id):
        self.window = window
        self.client_id = _client_id

    def isClientExist(self):
        subscriber_list = self.window.subscriberModel.GetSubscribers()
        for sub in subscriber_list:
            if sub["id"] == self.client_id:
                return True
        return False

    def clientNotFound(self):
        print("[Error] Client ID not found:", self.client_id)

    def SendCommandForward(self):
        if self.isClientExist():
            # Send forward command
            pass
        else:
            self.clientNotFound()

    def SendCommandBackward(self):
        if self.isClientExist():
            # Send backward command
            pass
        else:
            self.clientNotFound()

    def SendCommandLeft(self):
        if self.isClientExist():
            # Send left command
            pass
        else:
            self.clientNotFound()

    def SendCommandRight(self):
        if self.isClientExist():
            # Send right command
            pass
        else:
            self.clientNotFound()

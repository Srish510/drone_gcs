from pymavlink import mavutil

class MAVLinkHandler:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.master = mavutil.mavlink_connection(self.connection_string)
        self.master.wait_heartbeat()

    def send_message(self, message):
        self.master.mav.send(message)

    def receive_message(self):
        message = self.master.recv_match(blocking=True)
        return message

    def close_connection(self):
        self.master.close()
from tkinter import StringVar

class TelemetryController:
    def __init__(self, telemetry_data):
        self.telemetry_data = telemetry_data
        self.altitude = StringVar()
        self.speed = StringVar()
        self.battery_status = StringVar()

    def update_telemetry(self):
        self.altitude.set(self.telemetry_data.get('altitude', 'N/A'))
        self.speed.set(self.telemetry_data.get('speed', 'N/A'))
        self.battery_status.set(self.telemetry_data.get('battery_status', 'N/A'))

    def get_altitude(self):
        return self.altitude.get()

    def get_speed(self):
        return self.speed.get()

    def get_battery_status(self):
        return self.battery_status.get()
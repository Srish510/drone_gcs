class Waypoint:
    def __init__(self, latitude, longitude, altitude, action=None):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.action = action

    def __repr__(self):
        return f"Waypoint(lat={self.latitude}, lon={self.longitude}, alt={self.altitude}, action={self.action})"

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "action": self.action
        }
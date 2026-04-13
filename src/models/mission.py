class Mission:
    def __init__(self):
        self.waypoints = []
        self.parameters = {}

    def add_waypoint(self, waypoint):
        self.waypoints.append(waypoint)

    def set_parameters(self, params):
        self.parameters.update(params)

    def get_mission_data(self):
        return {
            "waypoints": [waypoint.get_data() for waypoint in self.waypoints],
            "parameters": self.parameters
        }
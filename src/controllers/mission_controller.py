class MissionController:
    def __init__(self, mission_model, drone_controller):
        self.mission_model = mission_model
        self.drone_controller = drone_controller

    def start_mission(self):
        for waypoint in self.mission_model.waypoints:
            self.drone_controller.navigate_to(waypoint)
            self.wait_for_arrival(waypoint)

    def wait_for_arrival(self, waypoint):
        while not self.drone_controller.is_at_waypoint(waypoint):
            pass  

    def abort_mission(self):
        self.drone_controller.stop()
        

    def update_mission(self, new_mission):
        self.mission_model = new_mission
        
class DroneState:
    def __init__(self, position=(0.0, 0.0, 0.0), velocity=(0.0, 0.0, 0.0), status='disconnected'):
        self.position = position  # (x, y, z) coordinates
        self.velocity = velocity  # (vx, vy, vz) velocity components
        self.status = status      # Status of the drone (e.g., 'connected', 'disconnected', 'flying', etc.)

    def update_position(self, new_position):
        self.position = new_position

    def update_velocity(self, new_velocity):
        self.velocity = new_velocity

    def update_status(self, new_status):
        self.status = new_status

    def get_state(self):
        return {
            'position': self.position,
            'velocity': self.velocity,
            'status': self.status
        }
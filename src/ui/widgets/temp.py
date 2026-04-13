import customtkinter as ctk
from tkintermapview import TkinterMapView

class LiveMap(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create Map Widget
        self.map_widget = TkinterMapView(self, corner_radius=10)
        self.map_widget.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={z}")

        # Set default view (e.g., center of the world or a specific home location)
        self.map_widget.set_zoom(15)
        self.map_widget.set_position(0.0, 0.0) 

        # State variables
        self.drone_marker = None
        self.path_points = []
        self.drone_path = None

    def update_position(self, lat, lon):
        """Updates the drone's position on the map and draws the flight path."""
        if lat == 0.0 and lon == 0.0:
            return  # Ignore invalid/initial GPS data

        # 1. Update or Create Marker
        if self.drone_marker is None:
            self.drone_marker = self.map_widget.set_marker(lat, lon, text="Drone")
            # Center map on the first valid coordinate received
            self.map_widget.set_position(lat, lon)
        else:
            self.drone_marker.set_position(lat, lon)

        # 2. Update Path
        self.path_points.append((lat, lon))
        
        # Only draw path if we have at least 2 points
        if len(self.path_points) > 1:
            if self.drone_path is None:
                self.drone_path = self.map_widget.set_path(self.path_points, color="blue", width=3)
            else:
                self.drone_path.set_position_list(self.path_points)

    def clear_path(self):
        """Clears the current path (useful when starting a new mission)."""
        if self.drone_path:
            self.drone_path.delete()
            self.drone_path = None
        self.path_points = []
import collections
import customtkinter as ctk
from tkinter import Canvas
from tkintermapview import TkinterMapView
from config.settings import Config  

class LiveMap(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if Config.GPS_ACTIVE:
            self._setup_global_map()
        else:
            self._setup_local_grid()

    #GLOBAL MAP LOGIC (GPS ACTIVE)
    def _setup_global_map(self):
        self.map_type = "GLOBAL"
        self.map_widget = TkinterMapView(self, corner_radius=10)
        self.map_widget.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        if hasattr(Config, 'MAP_TILE_SERVER'):
            self.map_widget.set_tile_server(Config.MAP_TILE_SERVER)
            
        self.map_widget.set_position(Config.HOME_LAT, Config.HOME_LON)
        self.map_widget.set_zoom(Config.DEFAULT_ZOOM)

        self.drone_marker = None
        self.path_points = []
        self.drone_path = None

    #LOCAL GRID LOGIC (GPS INACTIVE)
    def _setup_local_grid(self):
        self.map_type = "LOCAL"
        self.TRAIL_MAX = 500
        self.BG        = "#0d0d1a"
        self.GRID_CLR  = "#1a1a30"
        self.GCS_CLR   = "#22c55e"
        self.DRONE_CLR = "#ff6b6b"
        self.TRAIL_CLR = "#3a7abf"
        self.TEXT_CLR  = "#556677"

        self._gcs_pos = (0.0, 0.0)
        self._drone_pos = (0.0, 0.0)
        self._trail = collections.deque(maxlen=self.TRAIL_MAX)
        self._scale = 1.0
        self._margin = 40

        self._canvas = Canvas(self, bg=self.BG, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self._canvas.bind("<Configure>", lambda _: self._redraw_grid())

    #UPDATE LOGIC
    def update_position(self, lat=0.0, lon=0.0, north=0.0, east=0.0):
        """
        Updates the map. 
        If GPS_ACTIVE: uses lat/lon. 
        If not GPS_ACTIVE: uses north/east (meters from GCS).
        """
        if Config.GPS_ACTIVE:
            self._update_global(lat, lon)
        else:
            self._update_local(north, east)


    def _update_global(self, lat, lon):
        if lat == 0.0 and lon == 0.0: return
        
        if self.drone_marker is None:
            self.drone_marker = self.map_widget.set_marker(lat, lon, text="Drone")
            self.map_widget.set_position(lat, lon)
        else:
            self.drone_marker.set_position(lat, lon)

        self.path_points.append((lat, lon))
        if len(self.path_points) > 1:
            if self.drone_path is None:
                self.drone_path = self.map_widget.set_path(self.path_points, color="blue", width=3)
            else:
                self.drone_path.set_position_list(self.path_points)

    def _update_local(self, north, east):
        self._drone_pos = (north, east)
        self._trail.append((north, east))
        self._redraw_grid()

    def _redraw_grid(self):
        c = self._canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 10 or h < 10: return

        m = self._margin
        plot_w, plot_h = w - 2 * m, h - 2 * m
        
        # Calculate scaling
        pts = list(self._trail) + [self._gcs_pos, self._drone_pos]
        n_pts, e_pts = [p[0] for p in pts], [p[1] for p in pts]
        n_min, n_max = min(n_pts), max(n_pts)
        e_min, e_max = min(e_pts), max(e_pts)

        span = max(max(n_max - n_min, 1.0), max(e_max - e_min, 1.0)) * 1.2
        self._scale = span / min(plot_w, plot_h)

        cx_off, cy_off = (e_min + e_max) / 2, (n_min + n_max) / 2

        def to_px(n, e):
            px = m + plot_w / 2 + (e - cx_off) / self._scale
            py = m + plot_h / 2 - (n - cy_off) / self._scale
            return px, py

        # Draw Grid
        for x in range(0, w, 40): c.create_line(x, 0, x, h, fill=self.GRID_CLR)
        for y in range(0, h, 40): c.create_line(0, y, w, y, fill=self.GRID_CLR)

        # Draw Trail
        if len(self._trail) > 1:
            coords = []
            for n, e in self._trail: coords.extend(to_px(n, e))
            c.create_line(*coords, fill=self.TRAIL_CLR, width=2, smooth=True)

        # Draw Markers
        gx, gy = to_px(*self._gcs_pos)
        c.create_rectangle(gx-6, gy-6, gx+6, gy+6, fill=self.GCS_CLR, outline="white")
        
        dx, dy = to_px(*self._drone_pos)
        c.create_oval(dx-5, dy-5, dx+5, dy+5, fill=self.DRONE_CLR, outline="white")
        
        # Connection line
        c.create_line(gx, gy, dx, dy, fill="#444444", dash=(4, 4))
        c.create_text(w-10, h-10, anchor="se", text=f"Scale: {self._scale:.2f} m/px", fill=self.TEXT_CLR)
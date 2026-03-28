"""
NOTE: This module is still in development.
"""

import collections
from tkinter import Frame, Canvas
import customtkinter as ctk


class LiveMap(Frame):

    TRAIL_MAX = 500           # max breadcrumb points
    BG        = "#0d0d1a"
    GRID_CLR  = "#1a1a30"
    GCS_CLR   = "#22c55e"     # green
    DRONE_CLR = "#ff6b6b"     # red
    TRAIL_CLR = "#3a7abf"   # muted blue
    TEXT_CLR  = "#556677"

    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=self.BG, **kwargs)

        self._gcs_pos = (0.0, 0.0)              # (north, east) m
        self._drone_pos = (0.0, 0.0)            # (north, east) m
        self._trail: collections.deque[tuple[float, float]] = collections.deque(
            maxlen=self.TRAIL_MAX
        )
        self._scale = 1.0                        # m per pixel (auto)
        self._margin = 40                        # px border

        self._build_ui()

    #UI:
    def _build_ui(self):
        header = ctk.CTkLabel(self, text="Live Map",
                              font=ctk.CTkFont(size=12, weight="bold"))
        header.pack(pady=(6, 2))

        self._canvas = Canvas(self, bg=self.BG, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self._canvas.bind("<Configure>", lambda _: self._redraw())

    #Public API:
    def update_drone_position(self, north: float, east: float):
        
        self._drone_pos = (north, east)
        self._trail.append((north, east))
        self._redraw()

    def set_gcs_position(self, north: float, east: float):
        self._gcs_pos = (north, east)
        self._redraw()

    def clear_trail(self):
        self._trail.clear()
        self._redraw()

    #Internal drawing logic:
    def _redraw(self):
        c = self._canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return

        m = self._margin
        plot_w = w - 2 * m
        plot_h = h - 2 * m
        if plot_w < 10 or plot_h < 10:
            return

        # Gather all points to compute scale
        pts = list(self._trail)
        pts.append(self._gcs_pos)
        pts.append(self._drone_pos)
        norths = [p[0] for p in pts]
        easts  = [p[1] for p in pts]
        n_min, n_max = min(norths), max(norths)
        e_min, e_max = min(easts), max(easts)

        span_n = max(n_max - n_min, 1.0)
        span_e = max(e_max - e_min, 1.0)
        # Keep square aspect and add 20 % padding
        span = max(span_n, span_e) * 1.2
        self._scale = span / min(plot_w, plot_h)

        cx_off = (e_min + e_max) / 2
        cy_off = (n_min + n_max) / 2

        def to_px(north, east):
            px = m + plot_w / 2 + (east - cx_off) / self._scale
            py = m + plot_h / 2 - (north - cy_off) / self._scale
            return px, py

        # Grid lines
        spacing = 40
        for x in range(0, w, spacing):
            c.create_line(x, 0, x, h, fill=self.GRID_CLR, tags="bg")
        for y in range(0, h, spacing):
            c.create_line(0, y, w, y, fill=self.GRID_CLR, tags="bg")

        # Scale indicator
        c.create_text(w - 6, h - 6, anchor="se",
                      text=f"1 px ≈ {self._scale:.2f} m",
                      fill=self.TEXT_CLR, font=("Consolas", 8), tags="bg")

        # Trail
        if len(self._trail) > 1:
            coords = []
            for n, e in self._trail:
                coords.extend(to_px(n, e))
            c.create_line(*coords, fill=self.TRAIL_CLR, width=2,
                          smooth=True, tags="trail")

        # GCS marker (bottom-left-ish, square)
        gx, gy = to_px(*self._gcs_pos)
        sz = 6
        c.create_rectangle(gx - sz, gy - sz, gx + sz, gy + sz,
                           fill=self.GCS_CLR, outline="#ffffff", width=1, tags="gcs")
        c.create_text(gx, gy + sz + 8, text="GCS", fill=self.GCS_CLR,
                      font=("Consolas", 8, "bold"), tags="gcs")

        # Drone marker (circle)
        dx, dy = to_px(*self._drone_pos)
        dr = 5
        c.create_oval(dx - dr, dy - dr, dx + dr, dy + dr,
                      fill=self.DRONE_CLR, outline="#ffffff", width=1, tags="drone")
        c.create_text(dx, dy - dr - 8, text="DRONE", fill=self.DRONE_CLR,
                      font=("Consolas", 8, "bold"), tags="drone")

        # Line connecting GCS → drone
        c.create_line(gx, gy, dx, dy, fill="#444444", dash=(4, 4),
                      width=1, tags="link")

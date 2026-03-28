import time
import collections
from tkinter import Frame

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AttitudeGraph(Frame):     #A real-time line graph showing roll, pitch, and yaw over time. Uses a rolling window to display only the most recent data points.

    MAX_POINTS = 200          # rolling window size

    COLORS = {
        "roll":  "#ff6b6b",   # red
        "pitch": "#51cf66",   # green
        "yaw":   "#339af0",   # blue
    }

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#1a1a2e")

        self._t0 = time.time()

        # Data buffers (deques auto-trim to MAX_POINTS)
        self._times  = collections.deque(maxlen=self.MAX_POINTS)
        self._roll   = collections.deque(maxlen=self.MAX_POINTS)
        self._pitch  = collections.deque(maxlen=self.MAX_POINTS)
        self._yaw    = collections.deque(maxlen=self.MAX_POINTS)

        self._build_chart()


    def _build_chart(self):
        self._fig = Figure(figsize=(5, 3), dpi=100, facecolor="#1a1a2e")
        self._ax = self._fig.add_subplot(111)

        # Styling
        self._ax.set_facecolor("#0d0d1a")
        self._ax.set_title("Roll / Pitch / Yaw", color="#cccccc",
                           fontsize=11, fontweight="bold", pad=8)
        self._ax.set_xlabel("Time (s)", color="#888888", fontsize=9)
        self._ax.set_ylabel("Degrees (°)", color="#888888", fontsize=9)
        self._ax.tick_params(colors="#666666", labelsize=8)
        for spine in self._ax.spines.values():
            spine.set_color("#333333")
        self._ax.grid(True, color="#222244", linewidth=0.5, linestyle="--")

        # Initial empty lines
        (self._line_roll,)  = self._ax.plot([], [], color=self.COLORS["roll"],
                                            linewidth=1.4, label="Roll")
        (self._line_pitch,) = self._ax.plot([], [], color=self.COLORS["pitch"],
                                            linewidth=1.4, label="Pitch")
        (self._line_yaw,)   = self._ax.plot([], [], color=self.COLORS["yaw"],
                                            linewidth=1.4, label="Yaw")

        self._ax.legend(loc="upper left", fontsize=8, facecolor="#1a1a2e",
                        edgecolor="#333333", labelcolor="#cccccc")
        self._fig.tight_layout(pad=1.5)

        # Embed in tkinter
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        
        

    #Public methods:
    def update_attitude(self, roll: float, pitch: float, yaw: float):   #Add a new attitude data point and update the graph
        
        t = time.time() - self._t0
        self._times.append(t)
        self._roll.append(roll)
        self._pitch.append(pitch)
        self._yaw.append(yaw)

        ts = list(self._times)
        self._line_roll.set_data(ts, list(self._roll))
        self._line_pitch.set_data(ts, list(self._pitch))
        self._line_yaw.set_data(ts, list(self._yaw))

        self._ax.set_xlim(ts[0], ts[-1] + 0.5)
        all_vals = list(self._roll) + list(self._pitch) + list(self._yaw)
        if all_vals:
            lo, hi = min(all_vals), max(all_vals)
            margin = max((hi - lo) * 0.15, 5)
            self._ax.set_ylim(lo - margin, hi + margin)

        self._canvas.draw_idle()


    def reset(self):        #Reset the graph and clear all data
        self._t0 = time.time()
        self._times.clear()
        self._roll.clear()
        self._pitch.clear()
        self._yaw.clear()
        self._line_roll.set_data([], [])
        self._line_pitch.set_data([], [])
        self._line_yaw.set_data([], [])
        self._canvas.draw_idle()

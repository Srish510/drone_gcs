from tkinter import Frame, Canvas

class MapView(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.init_ui()

    def init_ui(self):
        self.canvas = Canvas(self, bg='#1a1a2e')
        self.canvas.pack(fill='both', expand=True)

        # Draw a grid placeholder for the map
        self.canvas.bind('<Configure>', self._draw_grid)

    def _draw_grid(self, event=None):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        spacing = 40
        for x in range(0, w, spacing):
            self.canvas.create_line(x, 0, x, h, fill='#2a2a4a', tags="grid")
        for y in range(0, h, spacing):
            self.canvas.create_line(0, y, w, y, fill='#2a2a4a', tags="grid")
        # Center crosshair
        cx, cy = w // 2, h // 2
        self.canvas.create_line(cx - 15, cy, cx + 15, cy, fill='#00ff88', width=2, tags="grid")
        self.canvas.create_line(cx, cy - 15, cx, cy + 15, fill='#00ff88', width=2, tags="grid")
        self.canvas.create_text(cx, 20, text="MAP VIEW", fill='#556677', font=("Consolas", 12, "bold"), tags="grid")

    def update_drone_position(self, x, y):
        # Update the drone's position on the map
        self.canvas.delete("drone")
        self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='red', tags="drone")

    def update_flight_path(self, path):
        # Draw the flight path on the map
        for i in range(len(path) - 1):
            self.canvas.create_line(path[i], path[i + 1], fill='blue', width=2)
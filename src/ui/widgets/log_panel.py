import datetime
import customtkinter as ctk
from tkinter import END


class LogPanel(ctk.CTkFrame):

    # Colours for each log source
    TAG_COLORS = {
        "GCS":   "#5cb8ff",   #blue
        "DRONE": "#14e225",   #green
        "SYS":   "#d51313",   #red
    }

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._create_ui()


    #UI:
    def _create_ui(self):
        # Header row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=8, pady=(6, 2))

        title = ctk.CTkLabel(header_row, text="Logs",
                              font=ctk.CTkFont(size=13, weight="bold"))
        title.pack(side="left")

        self.clear_btn = ctk.CTkButton(header_row, text="Clear", width=60,
                                       height=24, fg_color="#444444",
                                       hover_color="#666666",
                                       command=self.clear)
        self.clear_btn.pack(side="right")

        # Filter buttons
        filter_row = ctk.CTkFrame(self, fg_color="transparent")
        filter_row.pack(fill="x", padx=8, pady=(0, 4))

        self._filter_var = ctk.StringVar(value="ALL")
        for tag in ("ALL", "GCS", "DRONE"):
            ctk.CTkRadioButton(filter_row, text=tag, variable=self._filter_var,
                               value=tag, command=self._apply_filter,
                               radiobutton_width=14, radiobutton_height=14,
                               font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 12))

        # Scrollable text area (use CTkTextbox for themed look)
        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=11),
                                      fg_color="#0d0d1a", text_color="#cccccc",
                                      wrap="word", state="disabled",
                                      height=140)
        self.textbox.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        for tag, color in self.TAG_COLORS.items():
            self.textbox._textbox.tag_configure(tag, foreground=color)

        self._logs: list[tuple[str, str, str]] = []


    #Pulic methods:
    def log(self, source: str, message: str):   #Add a log entry from GCS or DRONE
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._logs.append((source.upper(), ts, message))
        active_filter = self._filter_var.get()
        if active_filter == "ALL" or active_filter == source.upper():
            self._append_line(source.upper(), ts, message)

    def log_gcs(self, message: str):
        self.log("GCS", message)

    def log_drone(self, message: str):
        self.log("DRONE", message)

    def clear(self):
        self._logs.clear()
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", END)
        self.textbox.configure(state="disabled")


    #Private methods:
    def _append_line(self, source: str, ts: str, message: str):
        self.textbox.configure(state="normal")
        self.textbox.insert(END, f"[{ts}] ")
        # Insert source with colour tag
        tag = source if source in self.TAG_COLORS else None
        start = self.textbox._textbox.index("end-1c")
        self.textbox.insert(END, f"[{source}]")
        if tag:
            end = self.textbox._textbox.index("end-1c")
            self.textbox._textbox.tag_add(tag, start, end)
        self.textbox.insert(END, f" {message}\n")
        self.textbox.configure(state="disabled")
        self.textbox.see(END)

    def _apply_filter(self):
        active = self._filter_var.get()
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", END)
        self.textbox.configure(state="disabled")
        for source, ts, msg in self._logs:
            if active == "ALL" or active == source:
                self._append_line(source, ts, msg)

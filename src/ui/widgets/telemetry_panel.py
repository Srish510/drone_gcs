import customtkinter as ctk

class TelemetryPanel(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.master = master
        self.create_ui()

    def create_ui(self):
        tiny = ctk.CTkFont(size=10)
        val  = ctk.CTkFont(size=10, weight="bold")

        for c in range(6):
            self.columnconfigure(c, weight=1 if c % 2 else 0)

        r = 0
        #Row 0: Bat % + short bar
        self._bat_var = ctk.StringVar(value="100%")

        ctk.CTkLabel(self, text="Bat:", font=tiny, text_color="#888").grid(
            row=r, column=0, sticky="w", padx=(0, 1), pady=1)
        self._bat_label = ctk.CTkLabel(self, textvariable=self._bat_var, font=val,
                                       text_color="#22c55e")
        self._bat_label.grid(row=r, column=1, sticky="w", padx=(0, 4), pady=1)

        self._bat_bar = ctk.CTkProgressBar(self, height=6, width=80,
                                           progress_color="#22c55e",
                                           fg_color="#333333", corner_radius=3)
        self._bat_bar.set(1.0)
        self._bat_bar.grid(row=r, column=2, columnspan=4, sticky="ew", padx=(0, 0), pady=1)
        r += 1

        #Row 1: Alt | Spd
        self._alt_var = ctk.StringVar(value="0.0 m")
        self._spd_var = ctk.StringVar(value="0.0 m/s")

        ctk.CTkLabel(self, text="Alt:", font=tiny, text_color="#888").grid(
            row=r, column=0, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._alt_var, font=val,
                     text_color="#fff").grid(row=r, column=1, sticky="e", padx=(0, 6), pady=1)

        ctk.CTkLabel(self, text="Spd:", font=tiny, text_color="#888").grid(
            row=r, column=2, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._spd_var, font=val,
                     text_color="#fff").grid(row=r, column=3, sticky="e", padx=(0, 6), pady=1)
        r += 1

        #Row 2: Velocity  Vx | Vy | Vz
        self._vx_var = ctk.StringVar(value="0.00")
        self._vy_var = ctk.StringVar(value="0.00")
        self._vz_var = ctk.StringVar(value="0.00")

        ctk.CTkLabel(self, text="Vx:", font=tiny, text_color="#5cb8ff").grid(
            row=r, column=0, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._vx_var, font=val,
                     text_color="#ccc").grid(row=r, column=1, sticky="e", padx=(0, 6), pady=1)

        ctk.CTkLabel(self, text="Vy:", font=tiny, text_color="#5cb8ff").grid(
            row=r, column=2, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._vy_var, font=val,
                     text_color="#ccc").grid(row=r, column=3, sticky="e", padx=(0, 6), pady=1)

        ctk.CTkLabel(self, text="Vz:", font=tiny, text_color="#5cb8ff").grid(
            row=r, column=4, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._vz_var, font=val,
                     text_color="#ccc").grid(row=r, column=5, sticky="e", pady=1)
        r += 1

        #Row 3: Accel  Ax | Ay | Az
        self._ax_var = ctk.StringVar(value="0.00")
        self._ay_var = ctk.StringVar(value="0.00")
        self._az_var = ctk.StringVar(value="0.00")

        ctk.CTkLabel(self, text="Ax:", font=tiny, text_color="#ffa94d").grid(
            row=r, column=0, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._ax_var, font=val,
                     text_color="#ccc").grid(row=r, column=1, sticky="e", padx=(0, 6), pady=1)

        ctk.CTkLabel(self, text="Ay:", font=tiny, text_color="#ffa94d").grid(
            row=r, column=2, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._ay_var, font=val,
                     text_color="#ccc").grid(row=r, column=3, sticky="e", padx=(0, 6), pady=1)

        ctk.CTkLabel(self, text="Az:", font=tiny, text_color="#ffa94d").grid(
            row=r, column=4, sticky="w", padx=(0, 1), pady=1)
        ctk.CTkLabel(self, textvariable=self._az_var, font=val,
                     text_color="#ccc").grid(row=r, column=5, sticky="e", pady=1)


    #public methods:
    def update_telemetry(self, altitude=None, speed=None, battery=None,
                         vx=None, vy=None, vz=None,
                         ax=None, ay=None, az=None):
        if altitude is not None:
            self._alt_var.set(f"{altitude:.1f} m")
        if speed is not None:
            self._spd_var.set(f"{speed:.1f} m/s")
        if battery is not None:
            pct = max(-1, min(100, battery))
            self._bat_bar.set(pct / 100)
            self._bat_var.set(f"{pct:.0f}%")
            color = "#22c55e" if pct > 50 else "#eab308" if pct > 25 else "#ef4444"
            self._bat_bar.configure(progress_color=color)
            self._bat_label.configure(text_color=color)
            if pct == -1:       #No battery info available
                self._bat_bar.configure(progress_color="#555555")
                self._bat_label.configure(text_color="#555555")
                self._bat_var.set(" Info Unavailable")
        if vx is not None:
            self._vx_var.set(f"{vx:.2f}")
        if vy is not None:
            self._vy_var.set(f"{vy:.2f}")
        if vz is not None:
            self._vz_var.set(f"{vz:.2f}")
        if ax is not None:
            self._ax_var.set(f"{ax:.2f}")
        if ay is not None:
            self._ay_var.set(f"{ay:.2f}")
        if az is not None:
            self._az_var.set(f"{az:.2f}")
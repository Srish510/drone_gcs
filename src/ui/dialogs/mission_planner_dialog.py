import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MissionPlannerDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mission Planner")
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(fg_color="#1a1a2e")
        self.grab_set()
        self.after(10, self.focus_force)

        #Header:
        self.header = ctk.CTkLabel(
            self,
            text="Mission Planner",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e0e0e0",
        )
        self.header.pack(pady=(20, 5))

        self.separator = ctk.CTkFrame(self, height=2, fg_color="#3a3a5c")
        self.separator.pack(fill="x", padx=30, pady=(0, 15))

        #Input:
        self.waypoint_label = ctk.CTkLabel(
            self,
            text="Waypoint Coordinates:",
            font=ctk.CTkFont(size=14),
            text_color="#b0b0c8",
        )
        self.waypoint_label.pack(pady=(5, 2))

        self.waypoint_entry = ctk.CTkEntry(
            self,
            width=300,
            height=38,
            placeholder_text="e.g. 28.6139, 77.2090",
            font=ctk.CTkFont(size=13),
            corner_radius=8,
            border_color="#3a3a5c",
            fg_color="#16213e",
            text_color="#e0e0e0",
        )
        self.waypoint_entry.pack(pady=(2, 12))

        #Buttons:
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=5)

        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Add Waypoint",
            command=self.add_waypoint,
            width=160,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0f3460",
            hover_color="#1a5276",
        )
        self.add_button.pack(side="left", padx=8)

        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save Mission",
            command=self.save_mission,
            width=160,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#533483",
            hover_color="#6c3fa0",
        )
        self.save_button.pack(side="left", padx=8)

        #Status Label:
        self.status_var = ctk.StringVar()
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#7ec8e3",
        )
        self.status_label.pack(pady=(18, 10))



    def add_waypoint(self):
        waypoint = self.waypoint_entry.get()
        if waypoint:
            # Logic to add waypoint to the mission
            self.status_var.set(f"Waypoint {waypoint} added.")
            self.waypoint_entry.delete(0, "end")
        else:
            self.status_var.set("Please enter valid coordinates.")

    def save_mission(self):
        # Logic to save the mission
        self.status_var.set("Mission saved successfully.")
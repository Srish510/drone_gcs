import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WorkshopDialog(ctk.CTkToplevel):
    def __init__(self, parent, send_command_callback=None):
        super().__init__(parent)
        self.title("Mission Planner")
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(fg_color="#1a1a2e")
        self.grab_set()
        self.after(10, self.focus_force)
        self.send_command = send_command_callback

        #Header:
        self.header = ctk.CTkLabel(
            self,
            text="Start Team Mission",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#e0e0e0",
        )
        self.header.pack(pady=(20, 5))

        self.separator = ctk.CTkFrame(self, height=2, fg_color="#3a3a5c")
        self.separator.pack(fill="x", padx=30, pady=(0, 15))

        #Input:
        self.team_label = ctk.CTkLabel(
            self,
            text="Team Name:",
            font=ctk.CTkFont(size=14),
            text_color="#b0b0c8",
        )
        self.team_label.pack(pady=(5, 2))

        self.team_entry = ctk.CTkEntry(
            self,
            width=300,
            height=38,
            placeholder_text="e.g. alpha_01 if name is Alpha 01",
            font=ctk.CTkFont(size=13),
            corner_radius=8,
            border_color="#3a3a5c",
            fg_color="#16213e",
            text_color="#e0e0e0",
        )
        self.team_entry.pack(pady=(2, 12))

        #Buttons:
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=5)

        self.add_button = ctk.CTkButton(
            self.button_frame,
            text="Start Mission",
            command=self.start_team_mission,
            width=160,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0f3460",
            hover_color="#1a5276",
        )
        self.add_button.pack(side="left", padx=8)

        #Status Label:
        self.status_var = ctk.StringVar()
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#7ec8e3",
        )
        self.status_label.pack(pady=(18, 10))



    def start_team_mission(self):
        name = self.team_entry.get()
        if name:
            # Logic to add waypoint to the mission
            self.status_var.set(f"Command sent to start mission for team '{name}'.")
            self.team_entry.delete(0, "end")
            self.send_command("start_mission", {"name": name})
        else:
            self.status_var.set("Please enter valid team name.")
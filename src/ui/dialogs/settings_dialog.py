from tkinter import Toplevel, Label, Entry, Button, StringVar

class SettingsDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("300x200")

        self.setting1_var = StringVar()
        self.setting2_var = StringVar()

        self.create_widgets()

    def create_widgets(self):
        Label(self, text="Setting 1:").pack(pady=5)
        Entry(self, textvariable=self.setting1_var).pack(pady=5)

        Label(self, text="Setting 2:").pack(pady=5)
        Entry(self, textvariable=self.setting2_var).pack(pady=5)

        Button(self, text="Save", command=self.save_settings).pack(pady=20)

    def save_settings(self):
        # Logic to save settings goes here
        print(f"Setting 1: {self.setting1_var.get()}")
        print(f"Setting 2: {self.setting2_var.get()}")
        self.destroy()
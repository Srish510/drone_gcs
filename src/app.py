from ui.main_window import MainWindow

class DroneGCSApp:
    def __init__(self):
        self.main_window = MainWindow()

    def run(self):
        self.main_window.mainloop()

if __name__ == "__main__":
    app = DroneGCSApp()
    app.run()
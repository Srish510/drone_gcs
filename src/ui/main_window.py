from tkinter import Menu
import customtkinter as ctk

from ui.widgets.telemetry_panel import TelemetryPanel
from ui.widgets.camera_feed import CameraFeed
from ui.widgets.attitude_graph import AttitudeGraph
from ui.widgets.image_send_panel import ImageSendPanel
from ui.widgets.live_map import LiveMap
from ui.widgets.log_panel import LogPanel
from ui.dialogs.connection_dialog import ConnectionDialog
from ui.dialogs.mission_planner_dialog import MissionPlannerDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.workshop_dialog import WorkshopDialog
from communication.telemetry_parser import parse_telemetry_data
from config.settings import Config


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(Config.WINDOW_TITLE)
        self.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Connection state
        self._connection = None          # SerialComm, UDPServer, or MAVLinkHandler
        self._conn_info = None           # dict with mode, port, etc.
        self._telemetry_poll_id = None   # after() id for telemetry polling

        self.create_layout()
    
    def create_layout(self):
        #Toolbar: (Top Buttons + connection status)
        toolbar = ctk.CTkFrame(self, height=40, corner_radius=0)
        toolbar.pack(fill="x", padx=0, pady=(0, 2))

        self.connect_btn = ctk.CTkButton(toolbar, text="Connect", width=100,
                                         command=self.open_connection_dialog)
        self.connect_btn.pack(side="left", padx=6, pady=4)

        self.arm_btn = ctk.CTkButton(toolbar, text="Arm", width=80,
                                     fg_color="#b8860b", hover_color="#daa520",
                                     command=self._cmd_arm)
        self.arm_btn.pack(side="left", padx=4, pady=4)

        self.takeoff_btn = ctk.CTkButton(toolbar, text="Take Off", width=80,
                                         fg_color="#2e8b57", hover_color="#3cb371",
                                         command=self._cmd_takeoff)
        self.takeoff_btn.pack(side="left", padx=4, pady=4)

        self.land_btn = ctk.CTkButton(toolbar, text="Land", width=80,
                                      fg_color="#cd5c5c", hover_color="#f08080",
                                      command=self._cmd_land)
        self.land_btn.pack(side="left", padx=4, pady=4)
        
        self.rtl_btn = ctk.CTkButton(toolbar, text="RTL", width=80,
                                      fg_color="#bd6711", hover_color="#f18810",
                                      command=self._cmd_rtl)
        self.rtl_btn.pack(side="left", padx=4, pady=4)
        
        self.mission_plan_btn = ctk.CTkButton(toolbar, text="Mission Planner", width=100,
                                      fg_color="#8111bd", hover_color="#c010f1",
                                      command=self.open_mission_planner)
        self.mission_plan_btn.pack(side="left", padx=4, pady=4)

        self.workshop_btn = ctk.CTkButton(toolbar, text="Workshop", width=80,
                                      fg_color="#1161bd", hover_color="#1071f1",
                                      command=self.open_workshop)
        self.workshop_btn.pack(side="left", padx=4, pady=4)

        #If needed, add new buttons here (before this) and implement their callbacks

        self.mode_label = ctk.CTkLabel(toolbar, text="Mode: STABILIZE",
                                       font=ctk.CTkFont(size=13, weight="bold"))
        self.mode_label.pack(side="right", padx=10, pady=4)

        self.conn_status = ctk.CTkLabel(toolbar, text="● Disconnected",
                                        text_color="#ff4444",
                                        font=ctk.CTkFont(size=12))
        self.conn_status.pack(side="right", padx=10, pady=4)


        #Body: (Attitude graph, live map, image send panel, telemetry, camera feed)
        body = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=0, pady=0)

        body.columnconfigure(0, weight=1)   # left column (graph row / image)
        body.columnconfigure(1, weight=1)   # middle column (graph row / live map)
        body.columnconfigure(2, weight=1)   # right sidebar
        body.rowconfigure(0, weight=2)      # graph row
        body.rowconfigure(1, weight=1)      # image-send + live-map row


        #Graph:
        self.attitude_graph = AttitudeGraph(body)
        self.attitude_graph.grid(row=0, column=0, columnspan=2, sticky="nsew",
                                 padx=(4, 2), pady=(4, 2))

        #Seed Image Send Panel:
        self.image_send_panel = ImageSendPanel(body)
        self.image_send_panel.grid(row=1, column=0, sticky="nsew", padx=(4, 2), pady=(2, 4))

        #Live Map:
        self.live_map = LiveMap(body)
        self.live_map.grid(row=1, column=1, sticky="nsew", padx=2, pady=(2, 4))

        #Right sidebar (camera feed + telemetry):
        sidebar = ctk.CTkFrame(body, width=320)
        sidebar.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(2, 4), pady=4)
        sidebar.grid_propagate(False)
        sidebar.rowconfigure(0, weight=1, minsize=400)   #camera feed
        sidebar.rowconfigure(1, weight=0)                # telemetry label
        sidebar.rowconfigure(2, weight=0)                # telemetry panel
        sidebar.columnconfigure(0, weight=1)

        #camera feed:
        self.camera_feed = CameraFeed(sidebar, fps=30)
        self.camera_feed.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 2))

        #Telemetry:
        telem_label = ctk.CTkLabel(sidebar, text="Telemetry",
                                   font=ctk.CTkFont(size=12, weight="bold"))
        telem_label.grid(row=1, column=0, sticky="w", padx=8, pady=(2, 0))
        self.telemetry_panel = TelemetryPanel(sidebar)
        self.telemetry_panel.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 4))

        #Default telemetry values
        self.telemetry_panel.update_telemetry(altitude=0.0, speed=0.0, battery=-1.0,
                                              vx=0.0, vy=0.0, vz=0.0,
                                              ax= 0.0, ay=0.0, az=0.0)

        #Logs:
        bottom = ctk.CTkFrame(self, corner_radius=0)
        bottom.pack(fill="x", padx=0, pady=(2, 0))

        self.log_panel = LogPanel(bottom, height=160)
        self.log_panel.pack(fill="x", padx=8, pady=(4, 2))

        # Write an initial log entry
        self.log_panel.log_gcs("GCS started — waiting for connection")


    #Callbacks for toolbar buttons:
    def open_connection_dialog(self):
        if self._connection is not None:
            self._disconnect()
            return
        ConnectionDialog(self)

    def open_mission_planner(self):
        MissionPlannerDialog(self)

    def open_settings(self):
        SettingsDialog(self)
        
    def open_workshop(self):
        WorkshopDialog(self, self._send_command)


    #Connection management:
    def on_connected(self, connection, conn_info: dict):
        """Called by ConnectionDialog after a successful connection."""
        self._connection = connection
        self._conn_info = conn_info
        mode = conn_info.get("mode", "unknown")

        # Update toolbar
        self.conn_status.configure(text="● Connected", text_color="#00ff88")
        self.connect_btn.configure(text="Disconnect")
        self.log_panel.log_gcs(f"Connected via {mode}")

        # Start telemetry polling for serial/UDP connections
        if mode in ("serial_rpi", "udp"):
            self._start_telemetry_poll()

        # Start camera feed receiver
        self._start_camera_feed(conn_info)


    def _disconnect(self):
        """Tear down the active connection."""
        # Stop telemetry polling
        if self._telemetry_poll_id is not None:
            self.after_cancel(self._telemetry_poll_id)
            self._telemetry_poll_id = None

        # Stop camera receiver
        self.camera_feed.stop_receiver()

        # Clear Map on Disconnect
        if hasattr(self.live_map, 'clear_trail'):
            self.live_map.clear_trail() # For local grid
        if hasattr(self.live_map, 'clear_path'):
            self.live_map.clear_path()  # For global map
            
            
        # Stop the connection
        if self._connection is not None:
            try:
                if hasattr(self._connection, 'stop'):
                    self._connection.stop()
                elif hasattr(self._connection, 'close_connection'):
                    self._connection.close_connection()
            except Exception as e:
                self.log_panel.log_gcs(f"Disconnect error: {e}")

        self._connection = None
        self._conn_info = None

        # Update toolbar
        self.conn_status.configure(text="● Disconnected", text_color="#ff4444")
        self.connect_btn.configure(text="Connect")
        self.mode_label.configure(text="Mode: STABILIZE")
        self.log_panel.log_gcs("Disconnected")

        # Reset telemetry display
        self.telemetry_panel.update_telemetry(altitude=0.0, speed=0.0, battery=-1.0,
                                              vx=0.0, vy=0.0, vz=0.0,
                                              ax=0.0, ay=0.0, az=0.0)


    #Telemetry polling:
    def _start_telemetry_poll(self):
        """Begin polling the connection for telemetry packets every 200ms."""
        self._poll_telemetry()

    def _poll_telemetry(self):
        if self._connection is None:
            return
        try:
            packet = self._connection.get_latest_packet()
            if packet:
                self._handle_packet(packet)
        except Exception as e:
            self.log_panel.log_gcs(f"Telemetry poll error: {e}")
        self._telemetry_poll_id = self.after(200, self._poll_telemetry)

    def _handle_packet(self, packet: dict):
        pkt_type = packet.get("type", "")
        print(packet)
        print(f"Received packet type: {pkt_type}")
        if pkt_type == "telemetry":
            parsed = parse_telemetry_data(packet["data"])
            self.telemetry_panel.update_telemetry(
                altitude=parsed.get('altitude', 0.0),
                speed=parsed.get('speed', 0.0),
                battery=parsed.get('battery', -1.0),
                vx=parsed.get('vx', 0.0),
                vy=parsed.get('vy', 0.0),
                vz=parsed.get('vz', 0.0),
                ax=parsed.get('ax', 0.0),
                ay=parsed.get('ay', 0.0),
                az=parsed.get('az', 0.0),
            )
            roll = parsed.get('roll', 0.0)
            pitch = parsed.get('pitch', 0.0)
            yaw = parsed.get('yaw', 0.0)
            mode = parsed.get('flight_mode', "UNKNOWN")

            self.live_map.update_position(
                lat=parsed.get('lat', 0.0),
                lon=parsed.get('lon', 0.0),
                north=parsed.get('north', 0.0), # meters from GCS
                east=parsed.get('east', 0.0)    # meters from GCS
            )
            self.attitude_graph.update_attitude(roll, pitch, yaw)

            if mode:
                self.mode_label.configure(text=f"Mode: {mode}")
            armed = parsed.get('armed', None)
            if armed is not None:
                self.arm_btn.configure(
                    text="Disarm" if armed else "Arm",
                    fg_color="#cd5c5c" if armed else "#b8860b"
                )

        else:
            self.log_panel.log_drone(f"Unknown packet: {pkt_type}")


    #Camera feed:
    def _start_camera_feed(self, conn_info: dict):
        """Start the camera feed receiver based on connection type."""
        mode = conn_info.get("mode", "")

        if mode == "serial_rpi":
            port = conn_info.get("port", "")
            self.camera_feed.start_receiver("serial", port=port, baudrate=921600)
            self.log_panel.log_gcs(f"Camera feed: serial on {port} @ 921600")

        elif mode == "udp":
            host = conn_info.get("host", "0.0.0.0")
            cam_port = conn_info.get("port", 14550) + 50
            self.camera_feed.start_receiver("udp", host=host, port=cam_port)
            self.log_panel.log_gcs(f"Camera feed: UDP on {host}:{cam_port}")

        elif mode == "tcp":
            host = conn_info.get("host", "0.0.0.0")
            cam_port = conn_info.get("port", 5760) + 50
            self.camera_feed.start_receiver("tcp", host=host, port=cam_port)
            self.log_panel.log_gcs(f"Camera feed: TCP on {host}:{cam_port}")


    #Command sending:
    def _send_command(self, command: str, params=None, log_text=None):
        if self._connection is None:
            self.log_panel.log_gcs(f"Cannot send '{command}' — not connected")
            return
        try:
            if hasattr(self._connection, 'send_command'):
                self._connection.send_command(command, params)
                display_text = log_text if log_text else command
                self.log_panel.log_gcs(f"Sent command: {display_text}")
            else:
                self.log_panel.log_gcs(f"Connection type does not support send_command")
        except Exception as e:
            self.log_panel.log_gcs(f"Command error: {e}")

    def _cmd_arm(self):
        is_armed = self.arm_btn.cget("text") == "Disarm"
        log_msg = "disarm" if is_armed else "arm"
        self._send_command("arm", log_text=log_msg)

    def _cmd_takeoff(self):
        self._send_command("takeoff", {"altitude": 4}, log_text="takeoff to 4m")

    def _cmd_land(self):
        self._send_command("land")

    def _cmd_rtl(self):
        self._send_command("rtl")

    def destroy(self):
        if self._connection is not None:
            self._disconnect()
        super().destroy()
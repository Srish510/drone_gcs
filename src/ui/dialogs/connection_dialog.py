from tkinter import messagebox
import customtkinter as ctk
import serial.tools.list_ports

from config.settings import Config

class ConnectionDialog:

    MODES = ["Serial", "MAVLink", "WiFi (UDP)", "WiFi (TCP)"]

    def __init__(self, parent):
        self.parent = parent
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Connect to Drone")
        self.dialog.geometry("400x380")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._result: dict | None = None      # filled on successful connect

        #Mode selector:
        ctk.CTkLabel(self.dialog, text="Connection Type",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(2, 4))

        self._mode_var = ctk.StringVar(value=self.MODES[0])
        self._mode_menu = ctk.CTkSegmentedButton(
            self.dialog, values=self.MODES, variable=self._mode_var,
            command=self._on_mode_change,
            font=ctk.CTkFont(size=11),
        )
        self._mode_menu.pack(fill="x", padx=16, pady=(0, 10))

        #Fields Container (dynamic):
        self._fields_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        self._fields_frame.pack(fill="both", expand=True, padx=16)

        #Variables:
        self._port_var = ctk.StringVar(value="")
        self._baud_var = ctk.StringVar(value="115200")
        self._host_var = ctk.StringVar(value="0.0.0.0")
        self._udp_port_var = ctk.StringVar(value="2000")
        self._udp_client_ip_var = ctk.StringVar(value="")
        self._tcp_host_var = ctk.StringVar(value="0.0.0.0")
        self._tcp_port_var = ctk.StringVar(value="5760")
        self._tcp_client_ip_var = ctk.StringVar(value="")

        self._build_fields()

        #Connect button:
        self._connect_btn = ctk.CTkButton(self.dialog, text="Connect", width=140,
                                          fg_color="#2e8b57", hover_color="#3cb371",
                                          command=self._connect)
        self._connect_btn.pack(pady=(8, 16))



    #Field Builders: (Private)
    def _clear_fields(self):
        for child in self._fields_frame.winfo_children():
            child.destroy()

    def _build_fields(self):
        self._clear_fields()
        mode = self._mode_var.get()
        if mode == self.MODES[0]:
            self._build_serial_rpi()
        elif mode == self.MODES[1]:
            self._build_serial_pixhawk()
        elif mode == self.MODES[2]:
            self._build_udp()
        else:
            self._build_tcp()

    def _on_mode_change(self, _value=None):
        self._build_fields()


    #Serial – RPi communication:
    def _build_serial_rpi(self):
        f = self._fields_frame
        ctk.CTkLabel(f, text="Serial port for direct RPi communication.",
                     font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", pady=(4, 6))

        ctk.CTkLabel(f, text="Port:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if ports:
            self._port_var.set(ports[0])
            ctk.CTkOptionMenu(f, variable=self._port_var, values=ports,
                              width=200).pack(anchor="w", pady=(2, 8))
        else:
            self._port_var.set("")
            ctk.CTkEntry(f, textvariable=self._port_var, width=200,
                         placeholder_text="e.g. COM3 or /dev/ttyUSB0").pack(anchor="w", pady=(2, 8))

        ctk.CTkLabel(f, text="Baud rate:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self._baud_var.set("57600")
        ctk.CTkOptionMenu(f, variable=self._baud_var,
                          values=["9600", "57600", "115200", "921600"],
                          width=200).pack(anchor="w", pady=(2, 4))
        ctk.CTkLabel(f, text="Use Baud 57600 for Radio", font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w")


    #Serial – Pixhawk (MAVLink):
    def _build_serial_pixhawk(self):
        f = self._fields_frame
        ctk.CTkLabel(f, text="MAVLink serial connection to Pixhawk.",
                     font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", pady=(4, 6))

        ctk.CTkLabel(f, text="Port:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if ports:
            self._port_var.set(ports[0])
            ctk.CTkOptionMenu(f, variable=self._port_var, values=ports,
                              width=200).pack(anchor="w", pady=(2, 8))
        else:
            self._port_var.set("")
            ctk.CTkEntry(f, textvariable=self._port_var, width=200,
                         placeholder_text="e.g. COM4 or /dev/ttyACM0").pack(anchor="w", pady=(2, 8))

        ctk.CTkLabel(f, text="Baud rate:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self._baud_var.set("57600")
        ctk.CTkOptionMenu(f, variable=self._baud_var,
                          values=["9600", "57600", "115200", "921600"],
                          width=200).pack(anchor="w", pady=(2, 4))
        ctk.CTkLabel(f, text="Use Baud 57600 for Radio", font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w")


    #WiFi (UDP):
    def _build_udp(self):
        f = self._fields_frame
        ctk.CTkLabel(f, text="UDP connection over WiFi.",
                     font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", pady=(4, 6))

        ctk.CTkLabel(f, text="Listen host:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(f, textvariable=self._host_var, width=200,
                     placeholder_text="0.0.0.0").pack(anchor="w", pady=(2, 8))

        ctk.CTkLabel(f, text="UDP port:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(f, textvariable=self._udp_port_var, width=200,
                     placeholder_text="2000").pack(anchor="w", pady=(2, 8))

        ctk.CTkLabel(f, text="Client IP (optional):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(f, textvariable=self._udp_client_ip_var, width=200,
                     placeholder_text="e.g. 192.168.1.100").pack(anchor="w", pady=(2, 4))


    #WiFi (TCP):
    def _build_tcp(self):
        f = self._fields_frame
        ctk.CTkLabel(f, text="TCP connection over WiFi.",
                     font=ctk.CTkFont(size=11), text_color="#888").pack(anchor="w", pady=(4, 6))

        ctk.CTkLabel(f, text="Host:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(f, textvariable=self._tcp_host_var, width=200,
                     placeholder_text="0.0.0.0").pack(anchor="w", pady=(2, 8))

        ctk.CTkLabel(f, text="TCP port:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(f, textvariable=self._tcp_port_var, width=200,
                     placeholder_text="5760").pack(anchor="w", pady=(2, 8))

        ctk.CTkLabel(f, text="Client IP (optional):", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(f, textvariable=self._tcp_client_ip_var, width=200,
                     placeholder_text="e.g. 192.168.1.100").pack(anchor="w", pady=(2, 4))
        

    #Connect button handler: (Logic)
    def _connect(self):
        mode = self._mode_var.get()

        if mode == self.MODES[0]:           # Serial – RPi
            port = self._port_var.get().strip()
            baud = self._baud_var.get().strip()
            if not port:
                messagebox.showerror("Error", "Please select or enter a serial port.", parent=self.dialog)
                return
            self._result = {"mode": "serial_rpi", "port": port, "baudrate": int(baud)}
            self._do_serial_rpi(port, int(baud))

        elif mode == self.MODES[1]:         # Serial – Pixhawk
            port = self._port_var.get().strip()
            baud = self._baud_var.get().strip()
            if not port:
                messagebox.showerror("Error", "Please select or enter a serial port.", parent=self.dialog)
                return
            self._result = {"mode": "serial_pixhawk", "port": port, "baudrate": int(baud)}
            self._do_serial_pixhawk(port, int(baud))

        elif mode == self.MODES[2]:          # WiFi (UDP)
            host = self._host_var.get().strip()
            port = self._udp_port_var.get().strip()
            client_ip = self._udp_client_ip_var.get().strip()
            if not host or not port:
                messagebox.showerror("Error", "Please enter host and port.", parent=self.dialog)
                return
            self._result = {"mode": "udp", "host": host, "port": int(port), "client_ip": client_ip or None}
            self._do_udp(host, int(port))

        else:                               # WiFi (TCP)
            host = self._tcp_host_var.get().strip()
            port = self._tcp_port_var.get().strip()
            client_ip = self._tcp_client_ip_var.get().strip()
            if not host or not port:
                messagebox.showerror("Error", "Please enter host and port.", parent=self.dialog)
                return
            self._result = {"mode": "tcp", "host": host, "port": int(port), "client_ip": client_ip or None}
            self._do_tcp(host, int(port))



    #Connection logic implementations: (Private)
    
    def _do_serial_rpi(self, port: str, baudrate: int):     #Serial connection to RPi
        try:
            from communication.serial_connection import SerialComm
            log_cb = self.parent.log_panel.log_gcs if hasattr(self.parent, 'log_panel') else None
            conn = SerialComm(port=port, baud=baudrate, log_callback=log_cb)
            if conn.is_connected():
                conn.start()
                self._result["connection"] = conn
                messagebox.showinfo("Success", f"Connected to RPi on {port} @ {baudrate}",
                                    parent=self.dialog)
                self.parent.on_connected(conn, self._result)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", f"Could not open {port}", parent=self.dialog)
        except Exception as exc:
            messagebox.showerror("Error", str(exc), parent=self.dialog)



    def _do_serial_pixhawk(self, port: str, baudrate: int):     #Serial MAVLink connection to Pixhawk
        try:
            from communication.mavlink_handler import MAVLinkHandler
            conn_str = f"{port}"  
            handler = MAVLinkHandler(conn_str)
            self._result["connection"] = handler
            messagebox.showinfo("Success",
                                f"MAVLink connected on {port} @ {baudrate}\n"
                                f"Heartbeat received.",
                                parent=self.dialog)
            self.parent.on_connected(handler, self._result)
            self.dialog.destroy()
        except Exception as exc:
            messagebox.showerror("Error", f"MAVLink connection failed:\n{exc}",
                                 parent=self.dialog)

    def _do_udp(self, host: str, port: int):        #UDP connection over WiFi
        try:
            from communication.udp_server import UDPServer
            log_cb = self.parent.log_panel.log_gcs if hasattr(self.parent, 'log_panel') else None
            client_ip = self._result.get("client_ip") or Config.DRONE_IP
            conn = UDPServer(host=host, port=port,
                             drone_ip=client_ip, drone_port=port,
                             log_callback=log_cb)
            if conn.is_connected():
                conn.start()
                self._result["connection"] = conn
                messagebox.showinfo("Success",
                                    f"UDP listening on {host}:{port}",
                                    parent=self.dialog)
                self.parent.on_connected(conn, self._result)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", f"Could not bind UDP {host}:{port}",
                                     parent=self.dialog)
        except Exception as exc:
            messagebox.showerror("Error", f"UDP connection failed:\n{exc}",
                                 parent=self.dialog)

    def _do_tcp(self, host: str, port: int):        #TCP connection over WiFi
        messagebox.showinfo("Info", "TCP connection not yet implemented.\nUse Serial or UDP.",
                            parent=self.dialog)

    #Public Varibles: 
    @property
    def result(self) -> dict | None:        #Connection params dict after a successful connect, else None.
        return self._result
import threading
import time
import serial
from utils.message_parser import json_to_dict, dict_to_json


class SerialComm:                #Handles low-level radio communication with the drone
    def __init__(self,
                 port=r"\\.\COM100",
                 baud=57600,
                 log_callback=None):
        self.port = port
        self.baud = baud
        self.serial = None
        self._log = log_callback or (lambda msg: print(msg))

        self._running = False
        self.listener_thread = None
        self._latest_packet = None
        self._packet_lock = threading.Lock()

        self._connect()


    def _connect(self) -> None:
        try:
            self.serial = serial.Serial(
                self.port,
                self.baud,
                timeout=0.05,
            )
        except Exception as e:
            self._log(f"[SerialComm] ERROR: {e}")
            self.serial = None


    def _send_json(self, data: dict) -> None:
        if not self.serial:
            return
        json_msg = dict_to_json(data, indent=None)
        if json_msg is None:
            self._log("[SerialComm] JSON generation failed")
            return
        try:
            self.serial.write((json_msg + "\n").encode("utf-8"))
        except Exception as e:
            self._log(f"[SerialComm] Send Error: {e}")


    def _listen_loop(self) -> None:
        buffer = ""
        while self._running:
            try:
                data = self.serial.read().decode("utf-8", errors="ignore")
                if not data:
                    continue
                buffer += data
                if "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    packet = json_to_dict(line)
                    if packet:
                        self._update_state(packet)
            except Exception as e:
                self._log(f"[SerialComm] Listen Error: {e}")
                time.sleep(0.5)

    def _update_state(self, packet: dict) -> None:
        with self._packet_lock:
            self._latest_packet = packet

    # Public Methods:

    def is_connected(self) -> bool:
        return self.serial is not None and self.serial.is_open

    def start(self) -> None:
        if not self.serial:
            self._log("[SerialComm] Cannot start — no serial connection")
            return
        self._running = True
        self.listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listener_thread.start()
        self._log("[SerialComm] Listener thread started")


    def stop(self) -> None:
        self._running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=2)
        if self.serial and self.serial.is_open:
            self.serial.close()
        self._log("[SerialComm] Stopped")
        

    def send_command(self, command: str, params=None) -> None:      #Send a command packet to the drone
        packet = {
            "type": "command",
            "command": command,
            "params": params or {},
            "timestamp": time.time()
        }
        self._send_json(packet)
        
        
    def send_image(self, image_data: bytes) -> None:
        if not self.serial:
            return
        try:
            self.serial.write(image_data)
        except Exception as e:
            self._log(f"[SerialComm] Image send error: {e}")


    def get_latest_packet(self) -> dict:
        with self._packet_lock:
            pkt = self._latest_packet
            self._latest_packet = None   
            return pkt
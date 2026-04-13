import socket
import threading
import time
import math
import struct
from utils.message_parser import json_to_dict, dict_to_json
from config.settings import Config


class UDPServer:                 # Handles UDP-based communication with the drone
    def __init__(self,
                 host="0.0.0.0",
                 port=14550,
                 drone_ip=Config.DRONE_IP,
                 drone_port=2000,
                 buffer_size=4096,
                 log_callback=None):
        self.host = host
        self.port = port
        self.drone_addr = (drone_ip, drone_port)
        self.buffer_size = buffer_size
        self.sock = None
        self._log = log_callback or (lambda msg: print(msg))

        self._running = False
        self.listener_thread = None
        self._latest_packet = None
        self._packet_lock = threading.Lock()

        self._connect()


    def _connect(self) -> None:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(0.05)
            self._log(f"[UDPServer] Bound to {self.host}:{self.port}")
        except Exception as e:
            self._log(f"[UDPServer] ERROR: {e}")
            self.sock = None


    def _send_json(self, data: dict, addr=None) -> None:
        if not self.sock:
            return
        target = addr or self.drone_addr
        json_msg = dict_to_json(data, indent=None)
        if json_msg is None:
            self._log("[UDPServer] JSON generation failed")
            return
        try:
            print(f"[UDPServer] Sending to {target}: {json_msg}")
            self.sock.sendto((json_msg + "\n").encode("utf-8"), target)
        except Exception as e:
            self._log(f"[UDPServer] Send Error: {e}")


    def _listen_loop(self) -> None:
        while self._running:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                if not data:
                    continue
                line = data.decode("utf-8", errors="ignore").strip()
                packet = json_to_dict(line)
                if packet:
                    self._update_state(packet)
            except socket.timeout:
                continue
            except Exception as e:
                self._log(f"[UDPServer] Listen Error: {e}")
                time.sleep(0.5)


    def _update_state(self, packet: dict) -> None:
        with self._packet_lock:
            self._latest_packet = packet

    # Public Methods:

    def is_connected(self) -> bool:
        return self.sock is not None

    def start(self) -> None:
        if not self.sock:
            self._log("[UDPServer] Cannot start — no UDP socket")
            return
        self._running = True
        self.listener_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listener_thread.start()
        self._log("[UDPServer] Listener thread started")

    def stop(self) -> None:
        self._running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=2)
        if self.sock:
            self.sock.close()
            self.sock = None
        self._log("[UDPServer] Stopped")

    def send_command(self, command: str, params=None) -> None:      # Send a command packet to the drone
        packet = {
            "type": "command",
            "command": command,
            "params": params or {},
            "timestamp": time.time()
        }
        self._send_json(packet)


    def send_image(self, image_data: bytes, addr=None) -> None:
        if not self.sock:
            return
        target = addr or self.drone_addr
        
        # Safe UDP payload size
        MAX_PAYLOAD_SIZE = 1024 
        
        total_size = len(image_data)
        total_chunks = math.ceil(total_size / MAX_PAYLOAD_SIZE)
        
        # Create a simple unique ID for this specific image (0-255)
        # This helps the receiver know which chunks belong to which image
        image_id = int(time.time() * 1000) % 256 
        
        try:
            for i in range(total_chunks):
                
                start = i * MAX_PAYLOAD_SIZE
                end = start + MAX_PAYLOAD_SIZE
                chunk_data = image_data[start:end]
                header = struct.pack(">3sBHH", b"IMG", image_id, i, total_chunks)

                packet = header + chunk_data
                self.sock.sendto(packet, target)
                print(f"[UDPServer] Sent chunk {i+1}/{total_chunks} for image ID {image_id} to {target}")

                time.sleep(0.002) 
                
            self._log(f"[UDPServer] Sent image {image_id} in {total_chunks} chunks.")
            
        except Exception as e:
            self._log(f"[UDPServer] Image send error: {e}")

    def get_latest_packet(self) -> dict:        # Retrieve and clear the latest received packet in a thread-safe manner
        with self._packet_lock:
            pkt = self._latest_packet
            self._latest_packet = None
            return pkt
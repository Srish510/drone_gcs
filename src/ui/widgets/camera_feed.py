'''
NOTE: This module is still in development - only UDP reception is currently implemented. 
The UDP receiver is designed to handle JPEG frames sent in multiple chunks, with a simple header protocol to reassemble them correctly. 
The serial and TCP receivers will be implemented in a future update, following similar principles of buffering and frame reconstruction as needed.
'''

import socket
import struct
import threading
import serial
from tkinter import Frame, Label

import cv2
import numpy as np
from PIL import Image, ImageTk
import customtkinter as ctk


class CameraFeed(Frame):

    def __init__(self, master=None, fps: int = 30, **kwargs):
        super().__init__(master, bg="#0d0d1a", **kwargs)
        self._delay = max(1, int(1000 / fps))
        self._photo = None          #prevent GC of last PhotoImage
        self._latest_frame = None   #numpy BGR frame
        self._running = False
        self._recv_thread: threading.Thread | None = None

        self._build_ui()
        self._poll()                #start the display loop (always runs)


    #UI:
    def _build_ui(self):
        self._header = ctk.CTkLabel(
            self, text="Drone Camera Feed",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._header.pack(pady=(8, 2))

        self._canvas = Label(self, bg="#0d0d1a", anchor="center",
                             text="Waiting for video…", fg="#555555",
                             font=("Consolas", 10))
        self._canvas.pack(fill="both", expand=True, padx=4, pady=(2, 4))

        self._status = ctk.CTkLabel(
            self, text="No source", font=ctk.CTkFont(size=10),
            text_color="#888888",
        )
        self._status.pack(pady=(0, 4))


    #Display loop:
    def _poll(self):        
        frame = self._latest_frame
        if frame is not None:
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                lw = max(self._canvas.winfo_width(), 1)
                lh = max(self._canvas.winfo_height(), 1)
                h, w = rgb.shape[:2]
                scale = min(lw / w, lh / h, 1.0)
                nw, nh = int(w * scale), int(h * scale)
                if nw > 0 and nh > 0:
                    rgb = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_AREA)
                img = Image.fromarray(rgb)
                self._photo = ImageTk.PhotoImage(img)
                self._canvas.configure(image=self._photo, text="")
            except Exception:
                pass
        self.after(self._delay, self._poll)


    #Push a frame for display: (Public)
    def push_frame(self, jpeg_bytes: bytes):    #Decodes JPEG and updates latest frame

        arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is not None:
            self._latest_frame = frame

    def push_raw_frame(self, bgr_array: np.ndarray):    #Queues an already-decoded BGR numpy array for display
        self._latest_frame = bgr_array


    #Start a background thread to receive frames from serial or network:
    def start_receiver(self, mode: str = "udp", **kwargs):
        """
        **kwargs :
            serial – ``port``, ``baudrate`` (default 921600)
            tcp    – ``host`` (default "0.0.0.0"), ``port`` (default 5600)
            udp    – ``host`` (default "0.0.0.0"), ``port`` (default 5600)
        """
        self.stop_receiver()
        self._running = True
        target = {
            "serial": self._recv_serial,
            "tcp":    self._recv_tcp,
            "udp":    self._recv_udp,
        }.get(mode)
        if target is None:
            self._status.configure(text=f"Unknown mode: {mode}", text_color="#ff4444")
            return
        self._recv_thread = threading.Thread(target=target, kwargs=kwargs,
                                             daemon=True, name="cam-recv")
        self._recv_thread.start()
        self._status.configure(text=f"Receiving ({mode})…", text_color="#00ff88")

    def stop_receiver(self):
        self._running = False
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join(timeout=2)
        self._recv_thread = None
        self._status.configure(text="Stopped", text_color="#888888")


    #Serial receiver: (Private)
    def _recv_serial(self, port: str = "COM3", baudrate: int = 921600, **_): #In Development

        try:
            ser = serial.Serial(port, baudrate, timeout=1)
        except Exception as exc:
            self._set_status_safe(f"Serial error: {exc}", "#ff4444")
            return

        self._set_status_safe(f"Serial {port} @ {baudrate}", "#00ff88")
        buf = bytearray()
        while self._running:
            chunk = ser.read(ser.in_waiting or 1)
            if not chunk:
                continue
            buf.extend(chunk)
            # Look for complete JPEG (SOI to EOI) in the buffer
            while True:
                soi = buf.find(b'\xff\xd8')
                if soi == -1:
                    buf.clear()
                    break
                eoi = buf.find(b'\xff\xd9', soi + 2)
                if eoi == -1:
                    if soi > 0:
                        del buf[:soi]
                    break
                jpeg = bytes(buf[soi:eoi + 2])
                del buf[:eoi + 2]
                self.push_frame(jpeg)
        ser.close()
        

    #UDP receiver: (Private)
    def _recv_udp(self, host: str = "0.0.0.0", port: int = 2050, **_): 
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        try:
            sock.bind((host, port))
        except Exception as exc:
            self._set_status_safe(f"UDP bind error: {exc}", "#ff4444")
            return

        self._set_status_safe(f"UDP listening {host}:{port}", "#00ff88")
        
        video_buffers = {}
        header_format = ">3sBHH"
        header_size = struct.calcsize(header_format)

        while self._running:
            try:
                data, addr = sock.recvfrom(65535)
                
                if not data or len(data) < header_size:
                    continue

                try:
                    magic, frame_id, chunk_index, total_chunks = struct.unpack(header_format, data[:header_size])
                except struct.error:
                    continue 
                if magic != b"VID":
                    continue
                    
                chunk_data = data[header_size:]
                
                stale_frames = [f_id for f_id in video_buffers.keys() if f_id != frame_id]
                for stale_id in stale_frames:
                    del video_buffers[stale_id]
                    
                if frame_id not in video_buffers:
                    video_buffers[frame_id] = {}
                    
                video_buffers[frame_id][chunk_index] = chunk_data

                if len(video_buffers[frame_id]) == total_chunks:
                    complete_jpeg_bytes = b"".join(
                        video_buffers[frame_id][i] for i in range(total_chunks)
                    )
                    del video_buffers[frame_id]
                    
                    self.push_frame(complete_jpeg_bytes)

            except socket.timeout:
                continue
            except Exception as e:
                pass
                
        sock.close()


    #TCP receiver
    def _recv_tcp(self, host: str = "0.0.0.0", port: int = 5600, **_): #In Development
        
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.settimeout(1)
        try:
            srv.bind((host, port))
            srv.listen(1)
        except Exception as exc:
            self._set_status_safe(f"TCP bind error: {exc}", "#ff4444")
            return

        self._set_status_safe(f"TCP listening {host}:{port}", "#00ff88")
        while self._running:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            self._set_status_safe(f"TCP client {addr[0]}", "#00ff88")
            conn.settimeout(2)
            try:
                while self._running:
                    header = self._recvall(conn, 4)
                    if header is None:
                        break
                    length = struct.unpack(">I", header)[0]
                    if length > 10_000_000: 
                        break
                    jpeg = self._recvall(conn, length)
                    if jpeg is None:
                        break
                    self.push_frame(jpeg)
            except Exception:
                pass
            finally:
                conn.close()
        srv.close()



    #Helpers:
    @staticmethod
    def _recvall(conn: socket.socket, n: int) -> bytes | None:
        buf = bytearray()
        while len(buf) < n:
            chunk = conn.recv(n - len(buf))
            if not chunk:
                return None
            buf.extend(chunk)
        return bytes(buf)


    def _set_status_safe(self, text: str, color: str):
        try:
            self.after(0, lambda: self._status.configure(text=text, text_color=color))
        except Exception:
            pass

    #Destruction:
    def destroy(self):
        self.stop_receiver()
        super().destroy()

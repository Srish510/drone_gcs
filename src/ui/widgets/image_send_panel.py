import os
import customtkinter as ctk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk


class ImageSendPanel(ctk.CTkFrame):

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._image_path: str | None = None
        self._photo_image = None  # prevent GC
        self._create_ui()


    #UI Setup:
    def _create_ui(self):
        header = ctk.CTkLabel(self, text="Send Image to Drone",
                              font=ctk.CTkFont(size=13, weight="bold"))
        header.pack(pady=(8, 4))

        # Preview canvas
        self.preview_canvas = Canvas(self, bg="#1a1a2e", highlightthickness=0,
                                     width=200, height=140)
        self.preview_canvas.pack(padx=8, pady=4, fill="x")
        self.preview_canvas.bind("<Configure>", self._redraw_preview)

        # File info label
        self.file_label = ctk.CTkLabel(self, text="No image selected",
                                       font=ctk.CTkFont(size=11),
                                       text_color="#888888")
        self.file_label.pack(padx=8, pady=(2, 4))

        # Buttons row
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=8, pady=(0, 8))

        self.browse_btn = ctk.CTkButton(btn_row, text="Browse…", width=90,
                                        command=self._browse_image)
        self.browse_btn.pack(side="left", padx=(0, 4))

        self.send_btn = ctk.CTkButton(btn_row, text="Send to Drone", width=110,
                                      fg_color="#2e8b57", hover_color="#3cb371",
                                      command=self._send_image, state="disabled")
        self.send_btn.pack(side="left", padx=(4, 0))

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11),
                                         text_color="#aaaaaa")
        self.status_label.pack(padx=8, pady=(0, 6))


    #Actions: (private)
    def _browse_image(self):        #Open dialog box to select pic
        path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._image_path = path
            self.file_label.configure(text=os.path.basename(path))
            self.send_btn.configure(state="normal")
            self._load_preview(path)


    def _load_preview(self, path: str): #Display selected image in the preview canvas
        try:
            img = Image.open(path)
            # Fit into preview canvas
            cw = max(self.preview_canvas.winfo_width(), 200)
            ch = max(self.preview_canvas.winfo_height(), 140)
            img.thumbnail((cw, ch), Image.LANCZOS)
            self._photo_image = ImageTk.PhotoImage(img)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(cw // 2, ch // 2,
                                             image=self._photo_image, anchor="center")
        except Exception as exc:
            self.status_label.configure(text=f"Preview error: {exc}", text_color="#ff4444")

    def _redraw_preview(self, _event=None):
        if self._image_path:
            self._load_preview(self._image_path)


    def _send_image(self):
        if not self._image_path:
            return
        self.status_label.configure(text="Sending…", text_color="#daa520")

        # Get the main window's active connection
        main_win = self.winfo_toplevel()
        connection = getattr(main_win, '_connection', None)
        if connection is None:
            self.status_label.configure(text="Not connected", text_color="#ff4444")
            return

        try:
            with open(self._image_path, "rb") as f:
                image_data = f.read()
            if hasattr(connection, 'send_image'):
                connection.send_image(image_data)
            self.after(100, self._on_send_complete)
        except Exception as exc:
            self.status_label.configure(text=f"Send error: {exc}", text_color="#ff4444")


    def _on_send_complete(self):
        self.status_label.configure(text="Image sent", text_color="#00ff88")
        # Fire a virtual event so the log panel can pick it up
        self.event_generate("<<ImageSent>>")


    #Public API:
    @property
    def image_path(self) -> str | None:
        return self._image_path
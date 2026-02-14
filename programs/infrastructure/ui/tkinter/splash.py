import tkinter as tk
from PIL import Image, ImageTk
import os

class SplashScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg="white")

        width = 400
        height = 300

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.canvas = tk.Canvas(self, width=width, height=height, bg="white", highlightthickness=0)
        self.canvas.pack()

        # Load background image
        img_path = os.path.join(os.path.dirname(__file__), "splash.png")
        if os.path.exists(img_path):
            self.bg_image = ImageTk.PhotoImage(Image.open(img_path))
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Overlay text
        self.canvas.create_text(
            width // 2,
            height // 2,
            text="String Search App\nLoading...",
            font=("Arial", 18, "bold"),
            justify="center",
            fill="black" # Ensure text is visible on white bg
        )

        self.update()

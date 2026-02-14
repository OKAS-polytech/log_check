import tkinter as tk

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

        # Placeholder for future image
        self.canvas = tk.Canvas(self, width=width, height=height, bg="white", highlightthickness=0)
        self.canvas.pack()

        self.canvas.create_text(width//2, height//2, text="String Search App\nLoading...", font=("Arial", 18), justify="center")

        self.update()

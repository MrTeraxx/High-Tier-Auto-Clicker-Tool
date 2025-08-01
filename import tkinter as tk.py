import tkinter as tk
import pyautogui
import time
import threading
import json
import os
from ctypes import windll
import win32con
import win32gui
import win32api
import keyboard

layout_file = "click_layout.json"


class OverlayApp:
    def __init__(self):
        self.click_points = []
        self.dots = []
        self.overlay = None
        self.overlay_canvas = None
        self.instruction = None
        self.stop_clicking_flag = False

        self.root = tk.Tk()
        self.root.title("Auto Clicker App")
        self.root.geometry("300x280")
        self.root.resizable(False, False)

        tk.Label(self.root, text="Auto Clicker Setup", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Start Selecting Points", command=self.start_overlay).pack(pady=5)
        tk.Button(self.root, text="Start Clicking", command=self.start_clicking_thread).pack(pady=5)
        tk.Button(self.root, text="Reset Saved Points", command=self.reset_points).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)

        self.status_label = tk.Label(self.root, text="", fg="green")
        self.status_label.pack(pady=5)

        self.load_layout()
        self.root.mainloop()

    def start_overlay(self):
        self.root.withdraw()
        time.sleep(0.5)
        self.overlay = tk.Toplevel()
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-transparentcolor', 'gray')
        self.overlay.config(bg='gray')

        self.overlay_canvas = tk.Canvas(self.overlay, bg='gray', highlightthickness=0)
        self.overlay_canvas.pack(fill='both', expand=True)

        self.make_window_click_blocking(self.overlay)

        self.overlay.bind("<Button-1>", self.record_click)
        self.overlay.bind("<Escape>", self.end_selection)

        self.instruction = tk.Label(self.overlay_canvas, text="Click to add points. Press ESC when done.",
                                    fg="white", bg="#444", font=("Segoe UI", 14))
        self.instruction.place(relx=0.5, rely=0.05, anchor='n')

    def make_window_click_blocking(self, win):
        win.update_idletasks()
        hwnd = win.winfo_id()
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, 0x000000, 180, win32con.LWA_ALPHA)

    def record_click(self, event):
        x, y = win32api.GetCursorPos()
        self.click_points.append((x, y))
        dot = self.overlay_canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='red')
        self.dots.append(dot)

    def end_selection(self, event=None):
        self.overlay.destroy()
        self.root.deiconify()
        self.save_layout()
        self.status_label.config(text=f"{len(self.click_points)} point(s) saved.")

    def start_clicking_thread(self):
        if not self.click_points:
            self.status_label.config(text="No points to click.")
            return

        self.stop_clicking_flag = False
        threading.Thread(target=self.start_clicking).start()
        self.status_label.config(text="Clicking started. Press ESC to stop.")
        keyboard.add_hotkey('esc', self.stop_clicking)

    def start_clicking(self):
        while not self.stop_clicking_flag:
            for x, y in self.click_points:
                if self.stop_clicking_flag:
                    break
                pyautogui.click(x, y)
                print(f"Clicked at: {x}, {y}")
                time.sleep(1)  # 1 second between clicks

    def stop_clicking(self):
        self.stop_clicking_flag = True
        self.status_label.config(text="Clicking stopped. Press Start to run again.")

    def save_layout(self):
        try:
            with open(layout_file, 'w') as f:
                json.dump(self.click_points, f)
        except Exception as e:
            print("Failed to save layout:", e)

    def load_layout(self):
        if os.path.exists(layout_file):
            try:
                with open(layout_file, 'r') as f:
                    self.click_points = json.load(f)
                self.status_label.config(text=f"{len(self.click_points)} saved point(s) loaded.")
            except Exception as e:
                print("Failed to load layout:", e)

    def reset_points(self):
        self.click_points = []
        if os.path.exists(layout_file):
            os.remove(layout_file)
        self.status_label.config(text="Saved points have been reset.")


if __name__ == "__main__":
    OverlayApp()

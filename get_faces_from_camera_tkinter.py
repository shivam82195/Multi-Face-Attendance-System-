import dlib
import numpy as np
import cv2
import os
import shutil
import logging
import tkinter as tk
from tkinter import filedialog
from tkinter import font as tkFont
from PIL import Image, ImageTk

# ---------- Hover Effects for Buttons ----------
def on_enter(e):
    e.widget['background'] = '#0056b3'  # Change on hover (active color)
    e.widget['foreground'] = 'white'

def on_leave(e):
    e.widget['background'] = e.widget._default_bg  # Reset to default color
    e.widget['foreground'] = e.widget._default_fg

class Face_Register:
    def __init__(self):
        self.existing_faces_cnt = 0
        self.input_name_char = ""
        self.uploaded_image_path = ""

        self.path_photos_from_camera = "data/data_faces_from_camera/"
        os.makedirs(self.path_photos_from_camera, exist_ok=True)

        self.win = tk.Tk()
        self.win.title("📷 Face Register")
        self.win.geometry("600x550")
        self.win.resizable(False, False)

        self.font_title = tkFont.Font(family='Helvetica', size=18, weight='bold')
        self.font_normal = tkFont.Font(family='Helvetica', size=12)
        self.font_button = tkFont.Font(family='Helvetica', size=12)

        self.build_gui()

    def build_gui(self):
        # Title
        tk.Label(self.win, text="🔒 Face Registration", font=self.font_title, bg="#f0f4f7", fg="#333").pack(pady=20)

        # Upload button
        self.upload_button = tk.Button(self.win, text="Step 1: Upload Image 📂", command=self.upload_image, font=self.font_button,
                                       bg="#007bff", fg="white", activebackground="#0056b3", relief="flat", width=20, height=2)
        self.upload_button._default_bg = "#007bff"
        self.upload_button._default_fg = "white"
        self.upload_button.bind("<Enter>", on_enter)
        self.upload_button.bind("<Leave>", on_leave)
        self.upload_button.pack(pady=10)

        # Image preview
        self.image_panel = tk.Label(self.win)
        self.image_panel.pack(pady=20)

        # Name input
        tk.Label(self.win, text="Step 2: Enter Name ✍️", font=self.font_normal, bg="#f0f4f7").pack()
        self.input_name = tk.Entry(self.win, width=30, font=self.font_normal, relief="solid", bd=1, fg="#333")
        self.input_name.pack(pady=5)

        # Register button
        self.register_button = tk.Button(self.win, text="Step 3: Register ✔️", command=self.register_student, font=self.font_button,
                                         bg="#28a745", fg="white", activebackground="#1e7e34", relief="flat", width=20, height=2)
        self.register_button._default_bg = "#28a745"
        self.register_button._default_fg = "white"
        self.register_button.bind("<Enter>", on_enter)
        self.register_button.bind("<Leave>", on_leave)
        self.register_button.pack(pady=15)

        # Log label
        self.log_label = tk.Label(self.win, text="", font=self.font_normal, fg="red", bg="#f0f4f7")
        self.log_label.pack(pady=10)

        # Set background color for the window
        self.win.configure(bg="#f0f4f7")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.uploaded_image_path = file_path
            # Display image
            image = Image.open(file_path)
            image = image.resize((200, 200))
            photo = ImageTk.PhotoImage(image)
            self.image_panel.config(image=photo)
            self.image_panel.image = photo  # Keep reference
            self.log_label["text"] = "Image uploaded. Now enter name."

    def register_student(self):
        name = self.input_name.get().strip()
        if not self.uploaded_image_path:
            self.log_label["text"] = "Please upload an image first!"
            return
        if not name:
            self.log_label["text"] = "Please enter a name!"
            return

        self.input_name_char = name
        self.existing_faces_cnt += 1
        folder_path = os.path.join(self.path_photos_from_camera, f"person_{self.existing_faces_cnt}_{name}")
        os.makedirs(folder_path, exist_ok=True)
        dest_path = os.path.join(folder_path, os.path.basename(self.uploaded_image_path))
        shutil.copy(self.uploaded_image_path, dest_path)

        self.log_label["text"] = f"Registered: {name}"
        logging.info("Saved image to: %s", dest_path)

        # Reset the fields
        self.input_name.delete(0, tk.END)
        self.uploaded_image_path = ""
        self.image_panel.config(image='')

    def run(self):
        self.win.mainloop()

def main():
    logging.basicConfig(level=logging.INFO)
    Face_Register().run()

if __name__ == '__main__':
    main()

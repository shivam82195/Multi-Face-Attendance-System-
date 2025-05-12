import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import threading
import webbrowser
from PIL import Image, ImageTk

USER_CREDENTIALS = {
    "admin": "admin"
}

# Global loading label
loading_label = None

# ---------- Styled Button Hover ----------
def on_enter(e):
    e.widget['background'] = '#0052cc'
    e.widget['foreground'] = 'white'

def on_leave(e):
    e.widget['background'] = '#007fff'
    e.widget['foreground'] = 'white'

# ---------- Verify Login ----------
def verify_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        login_window.destroy()
        show_menu()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

# ---------- Show Help Instructions ----------
def show_help():
    help_window = tk.Toplevel()
    help_window.title("Help - How to Use")
    help_window.geometry("450x400")
    help_window.configure(bg="white")

    instructions = (
        "📘 How to Use the Attendance System:\n\n"
        "1️ Register Students:\n"
        "   - Opens webcam to capture face images.\n"
        "   - Enter student name and ID when prompted.\n\n"
        "2️ Extract Features to CSV:\n"
        "   - Converts the captured face data to feature vectors.\n"
        "   - Stores them in a CSV file for future recognition.\n\n"
        "3️ Take Attendance:\n"
        "   - Opens webcam and recognizes students' faces.\n"
        "   - Marks present in the database.\n\n"
        "4️ View Attendance:\n"
        "   - Opens a browser showing attendance records.\n\n"
        "❗ Tip: Make sure you extract features before taking attendance.\n"
        "💾 All attendance data is stored in the database."
    )

    tk.Label(help_window, text=instructions, justify="left",
             font=("Arial", 11), bg="white", fg="#333", wraplength=420).pack(padx=10, pady=10)

# ---------- Show Main Menu ----------
def show_menu():
    global loading_label

    menu_window = tk.Tk()
    menu_window.title("Main Menu")
    menu_window.geometry("600x500")  # Wider to fit help button
    menu_window.configure(bg="#f0f4f8")

    tk.Label(menu_window, text="📋 Attendance System", font=("Helvetica", 20, "bold"), bg="#f0f4f8", fg="#333").pack(pady=20)

    def styled_button(text, command):
        btn = tk.Button(menu_window, text=text, font=("Arial", 12), width=30, height=2, bg="#007fff", fg="white", relief="flat", command=lambda: run_with_transition(command))
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.pack(pady=8)
        return btn

    styled_button("1. Register Students", run_get_faces)
    styled_button("2. Extract Features to CSV", run_features_extraction)
    styled_button("3. Take Attendance", run_attendance_taker)
    styled_button("4. View Attendance", run_view_attendance)

    tk.Button(menu_window, text="❌ Exit", command=menu_window.quit,
              font=("Arial", 12), width=30, height=2, bg="#ff4d4d", fg="white", relief="flat").pack(pady=15)

    loading_label = tk.Label(menu_window, text="", font=("Arial", 12, "italic"), bg="#f0f4f8", fg="blue")
    loading_label.pack(pady=5)

    # --- Help Button on the right ---
    help_btn = tk.Button(menu_window, text="❓ Help", command=show_help,
                         font=("Arial", 12), bg="#6c757d", fg="white", relief="flat", width=10)
    help_btn.place(x=470, y=20)  # Adjust X and Y to position right-top

    menu_window.mainloop()

# ---------- Threaded Task Launcher ----------
def run_with_transition(task_func):
    def wrapper():
        loading_label.config(text="⏳ Please wait...")
        task_func()
        loading_label.config(text="")

    thread = threading.Thread(target=wrapper)
    thread.start()

# ---------- Task Launchers ----------
def run_get_faces():
    run_script("get_faces_from_camera_tkinter.py", "Register Students")

def run_features_extraction():
    run_script("features_extraction_to_csv.py", "Feature Extraction")

def run_attendance_taker():
    run_script("attendance_taker.py", "Take Attendance")

def run_script(script_name, task_name):
    if os.path.exists(script_name):
        subprocess.run(["python", script_name])
    else:
        messagebox.showerror("Error", f"{task_name} script '{script_name}' not found!")

def run_view_attendance():
    def start_flask():
        subprocess.run(["python", "app.py"])
    threading.Thread(target=start_flask, daemon=True).start()
    webbrowser.open("http://127.0.0.1:5000")

# ---------- Login Window ----------
login_window = tk.Tk()
login_window.title("Login - JUIT Attendance System")
login_window.geometry("400x530")
login_window.configure(bg="#ffffff")

# --- Logo and Header ---
try:
    logo_img = Image.open("HomeLogo.jpg")
    logo_img = logo_img.resize((100, 100))
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(login_window, image=logo_photo, bg="#ffffff")
    logo_label.image = logo_photo
    logo_label.pack(pady=(20, 5))
except Exception as e:
    print("Logo loading failed:", e)

tk.Label(login_window, text="Jaypee University of Information Technology", font=("Helvetica", 13, "bold"), bg="#ffffff", fg="#0a4275").pack()
tk.Label(login_window, text="Multi-Face Attendance System", font=("Helvetica", 12), bg="#ffffff", fg="#222").pack(pady=(5, 10))

tk.Label(login_window, text="Made by:", font=("Arial", 10, "bold"), bg="#ffffff", fg="#555").pack()
tk.Label(login_window, text="Vaibhav Kumar Gupta (211183)\nShivam Thakur (211365)", font=("Arial", 10), bg="#ffffff", fg="#555").pack(pady=(0, 20))

# --- Login Fields ---
tk.Label(login_window, text="🔐 Admin Login", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333").pack(pady=10)

tk.Label(login_window, text="Username:", font=("Arial", 12), bg="#ffffff").pack()
username_entry = tk.Entry(login_window, font=("Arial", 12), width=25)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:", font=("Arial", 12), bg="#ffffff").pack()
password_entry = tk.Entry(login_window, show="*", font=("Arial", 12), width=25)
password_entry.pack(pady=5)

login_btn = tk.Button(login_window, text="Login", font=("Arial", 12, "bold"), bg="#28a745", fg="white", width=18, height=2, relief="flat", command=verify_login)
login_btn.pack(pady=25)

login_window.mainloop()

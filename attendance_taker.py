import dlib
import numpy as np
import cv2
import os
import pandas as pd
import time
import logging
import sqlite3
import datetime
from tkinter import Tk, filedialog, Button, Label

# ---------- Hover Effects for Buttons ----------
def on_enter(e):
    e.widget['background'] = '#0056b3'
def on_leave(e):
    e.widget['background'] = e.widget._default_bg

# Load Dlib models
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('data/data_dlib/shape_predictor_68_face_landmarks.dat')
face_reco_model = dlib.face_recognition_model_v1("data/data_dlib/dlib_face_recognition_resnet_model_v1.dat")

# Initialize database
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        name TEXT, 
        time TEXT, 
        date DATE, 
        UNIQUE(name, date)
    )
""")
conn.commit()
conn.close()

class FaceRecognizer:
    def __init__(self):
        self.face_features_known_list = []
        self.face_name_known_list = []
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def get_face_database(self):
        if os.path.exists("data/features_all.csv"):
            csv_rd = pd.read_csv("data/features_all.csv", header=None)
            for i in range(csv_rd.shape[0]):
                features = []
                self.face_name_known_list.append(csv_rd.iloc[i][0])
                for j in range(1, 129):
                    val = csv_rd.iloc[i][j]
                    features.append(float(val) if val != '' else 0.0)
                self.face_features_known_list.append(features)
            print(f"Loaded {len(self.face_features_known_list)} faces from database.")
            return True
        else:
            print("features_all.csv not found.")
            return False

    def return_euclidean_distance(self, feature_1, feature_2):
        return np.linalg.norm(np.array(feature_1) - np.array(feature_2))

    def mark_attendance(self, name):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE name = ? AND date = ?", (name, current_date))
        if cursor.fetchone() is None:
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            cursor.execute("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)",
                           (name, current_time, current_date))
            conn.commit()
            print(f"{name} marked present at {current_time}")
        else:
            print(f"{name} already marked present today.")
        conn.close()

    def recognize_faces(self, image):
        faces = detector(image, 1)
        for face in faces:
            shape = predictor(image, face)
            face_descriptor = face_reco_model.compute_face_descriptor(image, shape)
            distances = [self.return_euclidean_distance(face_descriptor, known)
                         for known in self.face_features_known_list]
            min_distance = min(distances)
            if min_distance < 0.4:
                name = self.face_name_known_list[distances.index(min_distance)]
                self.mark_attendance(name)
                color = (0, 255, 0)
            else:
                name = "Unknown"
                color = (0, 0, 255)
            cv2.putText(image, name, (face.left(), face.top() - 10), self.font, 0.8, color, 2)
            cv2.rectangle(image, (face.left(), face.top()), (face.right(), face.bottom()), (255, 255, 255), 2)
        return image

    def webcam_mode(self):
        cap = cv2.VideoCapture(0)
        window_name = "Face Recognizer"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = self.recognize_faces(frame)
            cv2.putText(frame, "📷 Webcam Mode (q: quit, u: upload)", (10, 30),
                        self.font, 0.7, (255, 255, 0), 2)
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('u'):
                cap.release()
                cv2.destroyAllWindows()
                self.image_upload_mode()
                break
        cap.release()
        cv2.destroyAllWindows()

    def image_upload_mode(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        root.destroy()
        if file_path:
            image = cv2.imread(file_path)
            image = self.recognize_faces(image)
            cv2.putText(image, "Image Upload Mode (any key to close)", (10, 30),
                        self.font, 0.7, (255, 255, 0), 2)
            cv2.imshow("Face Recognizer", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def run(self):
        if not self.get_face_database():
            return

        root = Tk()
        root.title("Attendance System - Select Mode")
        root.geometry("400x350")
        root.configure(bg="#f0f4f7")
        root.resizable(False, False)

        # Heading
        Label(root, text="🕵️‍♂️ Select Attendance Mode", font=("Helvetica", 16, "bold"),
              bg="#f0f4f7", fg="#333333").pack(pady=30)

        # Helper to create styled buttons
        def styled_btn(text, cmd, bg_color):
            btn = Button(root, text=text, font=("Helvetica", 12), width=24, height=2,
                         bg=bg_color, fg="white", relief="flat", command=lambda: [root.destroy(), cmd()])
            btn._default_bg = bg_color
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            btn.pack(pady=10)
            return btn

        styled_btn("📷  Webcam Mode", self.webcam_mode, "#007bff")
        styled_btn("📂  Upload Image", self.image_upload_mode, "#28a745")
        styled_btn("❌  Exit", root.destroy, "#dc3545")

        root.mainloop()

if __name__ == '__main__':
    recognizer = FaceRecognizer()
    recognizer.run()

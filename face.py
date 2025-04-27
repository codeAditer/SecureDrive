import cv2
import os
import pickle
import numpy as np
import json
import csv
import subprocess
from datetime import datetime, timedelta
from keras_facenet import FaceNet
from sklearn.metrics.pairwise import cosine_similarity
import pygame
from threading import Thread

# Initialize pygame mixer
pygame.mixer.init()

sound_path = "assets/alarm.wav"

def play_alarm():
    pygame.mixer.music.load(sound_path)  # Ensure this file exists
    pygame.mixer.music.play(-1)  # Loop indefinitely

def stop_alarm():
    pygame.mixer.music.stop()

# Load known embeddings
with open("face_embeddings.pkl", "rb") as f:
    all_embeddings = pickle.load(f)

# Load user profiles
with open("user_profiles.json", "r") as f:
    profiles = json.load(f)

# CSV setup
csv_file_path = os.path.join("user_logins", "user_logins.csv")
if not os.path.exists(csv_file_path):
    with open(csv_file_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Name", "Login Time", "Image Filename"])

# FaceNet and setup
embedder = FaceNet()
RECOGNITION_THRESHOLD = 0.7
unknown_start_time = None
unknown_captured = False
face_detected_time = None
user_authenticated_time = None
alarm_active = False

# Webcam setup
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

print("[INFO] Face Unlock System Running...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Update: No auto-quit after 30 seconds
    if len(faces) > 0 and face_detected_time is None:
        face_detected_time = datetime.now()
        print("[INFO] Face detected.")

    identity = "Unknown"
    max_sim = 0
    show_text = "No face detected"
    box_color = (0, 0, 255)

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]

        # Resize to FaceNet input
        face_resized = cv2.resize(face_img, (160, 160))

        # Enhance quality
        face_resized = cv2.GaussianBlur(face_resized, (3, 3), 0)
        lab = cv2.cvtColor(face_resized, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        face_resized = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

        # Convert to RGB for FaceNet
        rgb_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)

        embedding_result = embedder.extract(rgb_face, threshold=0.95)  # Ensure correct method is used here
        if embedding_result:
            embedding = embedding_result[0]['embedding']

            for user_id, user_embeds in all_embeddings.items():
                sim = cosine_similarity([embedding], user_embeds)
                highest = np.max(sim)
                if highest > max_sim and highest > RECOGNITION_THRESHOLD:
                    identity = user_id
                    max_sim = highest

        if identity != "Unknown":
            user = profiles.get(identity, {})
            show_text = f"{identity} | {user.get('name', 'N/A')}"
            box_color = (0, 255, 0)
            unknown_start_time = None
            unknown_captured = False

            if alarm_active:
                stop_alarm()
                alarm_active = False

            if user_authenticated_time is None:
                user_authenticated_time = datetime.now()
            elif (datetime.now() - user_authenticated_time).total_seconds() > 5:
                login_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                image_filename = f"user_{identity}_{timestamp}.jpg"
                image_path = os.path.join("user_logins", image_filename)

                cv2.imwrite(image_path, face_img)

                with open(csv_file_path, "a", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([identity, user.get("name", "N/A"), login_time_str, image_filename])

                with open("current_user.json", "w") as json_file:
                    json.dump({"user_id": identity}, json_file)

                print(f"[INFO] User {identity} authenticated. Launching dashboard...")

                stop_alarm()
                cap.release()
                cv2.destroyAllWindows()
                subprocess.Popen(["python", "dashboard.py"])
                subprocess.Popen(["python", "driver.py"])  # Corrected spelling of 'python'
                exit()

        else:
            now = datetime.now()
            if unknown_start_time is None:
                unknown_start_time = now
                unknown_captured = False
            elif not unknown_captured and (now - unknown_start_time) > timedelta(seconds=5):
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                filename_stamp = now.strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"unknown_{filename_stamp}.jpg"

                # Capture the full frame and save it
                cv2.putText(frame, timestamp, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 0), 2, cv2.LINE_AA)

                os.makedirs("unknown_faces", exist_ok=True)
                cv2.imwrite(os.path.join("unknown_faces", filename), frame)  # Save the full frame
                print(f"[ALERT] Unknown face captured: {filename}")

                if not alarm_active:
                    Thread(target=play_alarm).start()
                    alarm_active = True

                unknown_captured = True

            show_text = "Unknown"
            box_color = (0, 0, 255)
            user_authenticated_time = None

        cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
        cv2.putText(frame, show_text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2)

    cv2.imshow("Face Unlock System", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("[INFO] Manually exited.")
        break

cap.release()
cv2.destroyAllWindows()
stop_alarm()
print("[INFO] System shutdown complete.")

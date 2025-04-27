import cv2
import os
import json
import pickle
import time
import tkinter as tk
from tkinter import messagebox
from keras_facenet import FaceNet

# Constants
PROFILE_FILE = "user_profiles.json"
EMBEDDING_FILE = "face_embeddings.pkl"
DATASET_DIR = "dataset"
IMAGES_PER_USER = 50

# Load existing profiles and embeddings
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        profiles = json.load(f)
else:
    profiles = {}

if os.path.exists(EMBEDDING_FILE):
    with open(EMBEDDING_FILE, "rb") as f:
        all_embeddings = pickle.load(f)
else:
    all_embeddings = {}

# GUI setup
root = tk.Tk()
root.title("User Registration")

# Labels and entries
labels = ["User ID", "Full Name", "Email", "Phone", "Seat Position", "AC Temp.", "Playlist"]
entries = {}

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(root, width=30)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[label] = entry

def register_user():
    user_id = entries["User ID"].get().strip()
    name = entries["Full Name"].get().strip()
    email = entries["Email"].get().strip()
    phone = entries["Phone"].get().strip()
    seat = entries["Seat Position"].get().strip()
    ac_temp = entries["AC Temp."].get().strip()
    play = entries["Playlist"].get().strip()

    if not user_id or user_id in profiles:
        messagebox.showerror("Error", "Invalid or duplicate User ID.")
        return

    # Step 1: Save profile
    profiles[user_id] = {
        "name": name,
        "email": email,
        "phone": phone,
        "seat_position": seat,
        "ac_temp": ac_temp,
        "playlist": play
    }
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

    # Step 2: Capture face images
    user_folder = os.path.join(DATASET_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    count = 0

    messagebox.showinfo("Capture", "Starting face capture. Press 'q' to cancel.")
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face_img = frame[y:y+h, x:x+w]
            face_resized = cv2.resize(face_img, (160, 160))
            img_path = os.path.join(user_folder, f"{user_id}_{count}.jpg")
            cv2.imwrite(img_path, face_resized)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Image {count}/{IMAGES_PER_USER}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            time.sleep(0.3)  # ✅ Add delay between each capture

        cv2.imshow("Capturing", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= IMAGES_PER_USER:
            break

    cap.release()
    cv2.destroyAllWindows()

    # Step 3: Generate embeddings
    embedder = FaceNet()
    user_embeddings = []
    for file in os.listdir(user_folder):
        img_path = os.path.join(user_folder, file)
        img = cv2.imread(img_path)
        if img is None:
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = embedder.extract(rgb, threshold=0.95)
        if faces:
            user_embeddings.append(faces[0]["embedding"])

    if user_embeddings:
        all_embeddings[user_id] = user_embeddings
        with open(EMBEDDING_FILE, "wb") as f:
            pickle.dump(all_embeddings, f)
        messagebox.showinfo("Success", f"User {user_id} registered successfully!")
        root.destroy()  # ✅ Automatically close the GUI after registration
    else:
        messagebox.showerror("Error", "No faces found in the captured images.")

# Register button
register_btn = tk.Button(root, text="Register", command=register_user)
register_btn.grid(row=len(labels), column=0, columnspan=2, pady=10)

root.mainloop()

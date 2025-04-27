import tkinter as tk
from tkinter import messagebox
import json
import os
import subprocess
import csv
from PIL import Image, ImageTk

def load_current_user():
    try:
        with open("current_user.json", "r") as f:
            data = json.load(f)
            return data.get("user_id")
    except Exception as e:
        messagebox.showerror("Error", f"Could not load current user.\n{e}")
        return None

def load_user_profile(user_id):
    try:
        with open("user_profiles.json", "r") as f:
            profiles = json.load(f)
            return profiles.get(user_id)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load user profiles.\n{e}")
        return None

# --- Command Functions ---
def add_user():
    subprocess.Popen(["python", "subfolder/add_user.py"])

def delete_user():
    subprocess.Popen(["python", "subfolder/delete_user.py"])

def delete_access_logs():
    logs_path = os.path.join("user_logins", "user_logins.csv")
    if os.path.exists(logs_path):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all access logs?")
        if confirm:
            try:
                with open(logs_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["user_id", "name", "login_time", "image_file"])  # reset headers
                for file in os.listdir("user_logins"):
                    if file.lower().endswith((".jpg", ".png", ".jpeg")):
                        os.remove(os.path.join("user_logins", file))
                messagebox.showinfo("Success", "Access logs deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete access logs.\n{e}")

def view_access_logs():
    try:
        logs_path = os.path.join("user_logins", "user_logins.csv")
        if not os.path.exists(logs_path):
            messagebox.showinfo("Access Logs", "No logs found.")
            return

        top = tk.Toplevel(dashboard)
        top.title("Access Logs")
        top.geometry("420x500")
        top.configure(bg="#f0f0f0")
        top.resizable(False, False)

        canvas = tk.Canvas(top, borderwidth=0, background="#f0f0f0")
        frame = tk.Frame(canvas, background="#f0f0f0")
        vsb = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4, 4), window=frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_frame_configure)

        # Load logs into a list to allow modification
        logs = []
        with open(logs_path, newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                if len(row) >= 4:
                    logs.append(row)

        def delete_log(index):
            user_id, name, login_time, image_file = logs[index]
            image_path = os.path.join("user_logins", image_file)

            confirm = messagebox.askyesno("Delete Entry", f"Delete log for {name} at {login_time}?")
            if confirm:
                del logs[index]
                with open(logs_path, "w", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(logs)
                if os.path.exists(image_path):
                    os.remove(image_path)
                top.destroy()
                view_access_logs()

        # Display logs
        for i, (user_id, name, login_time, image_file) in enumerate(logs):
            log_frame = tk.Frame(frame, bg="#ffffff", bd=1, relief="solid", padx=10, pady=5)
            log_frame.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            image_path = os.path.join("user_logins", image_file)
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img.thumbnail((80, 80))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(log_frame, image=photo)
                img_label.image = photo
                img_label.grid(row=0, column=0, rowspan=3, padx=5)
            else:
                img_label = tk.Label(log_frame, text="[No Image]", width=10, bg="#ffffff")
                img_label.grid(row=0, column=0, rowspan=3, padx=5)

            tk.Label(log_frame, text=f"User ID: {user_id}", bg="#ffffff", anchor="w").grid(row=0, column=1, sticky="w")
            tk.Label(log_frame, text=f"Name: {name}", bg="#ffffff", anchor="w").grid(row=1, column=1, sticky="w")
            tk.Label(log_frame, text=f"Login Time: {login_time}", bg="#ffffff", anchor="w").grid(row=2, column=1, sticky="w")

            # X delete button (top-right)
            delete_btn = tk.Button(
                log_frame, text="❌", font=("Arial", 10),
                command=lambda idx=i: delete_log(idx),
                bg="#ffffff", fg="red", bd=0, activeforeground="darkred", cursor="hand2"
            )
            delete_btn.grid(row=0, column=2, sticky="ne", padx=2)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load logs: {e}")


def view_unknown_logs():
    folder = "unknown_faces"
    if not os.path.exists(folder):
        os.makedirs(folder)

    files = os.listdir(folder)
    image_files = sorted(
        [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg"))],
        reverse=True
    )

    if not image_files:
        messagebox.showinfo("Unknown Faces", "No unknown faces found.")
        return

    top = tk.Toplevel(dashboard)
    top.title("Unknown Faces")
    top.geometry("440x500")
    top.resizable(False, False)

    canvas = tk.Canvas(top, borderwidth=0, background="#ffffff")
    frame = tk.Frame(canvas, background="#ffffff")
    vsb = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4, 4), window=frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", on_frame_configure)

    thumbnails = []

    def show_full_image(img_path):
        img_win = tk.Toplevel(top)
        img_win.title("Full Image")
        img = Image.open(img_path)
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(img_win, image=photo)
        label.image = photo
        label.pack()

    def delete_image(file_name):
        file_path = os.path.join(folder, file_name)
        confirm = messagebox.askyesno("Delete Image", f"Are you sure you want to delete {file_name}?")
        if confirm:
            os.remove(file_path)
            top.destroy()
            view_unknown_logs()

    for i, file in enumerate(image_files):
        img_path = os.path.join(folder, file)
        try:
            img = Image.open(img_path)
            img.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(img)
            thumbnails.append(photo)

            cell = tk.Frame(frame, bg="#ffffff", bd=1, relief="solid")
            cell.grid(row=i // 2, column=i % 2, padx=10, pady=10)

            # ❌ Delete button (top-right)
            delete_btn = tk.Button(
                cell, text="❌", font=("Arial", 10), bg="#ffffff", fg="red",
                bd=0, activeforeground="darkred", cursor="hand2",
                command=lambda name=file: delete_image(name)
            )
            delete_btn.pack(anchor="ne", padx=2, pady=2)

            label = tk.Label(cell, image=photo, bg="#1e1e2f", cursor="hand2")
            label.image = photo
            label.pack()
            label.bind("<Button-1>", lambda e, path=img_path: show_full_image(path))

            filename = tk.Label(cell, text=file, font=("Arial", 8), bg="#1e1e2f", fg="white")
            filename.pack()

        except Exception as e:
            print(f"Error loading image {file}: {e}")

    top.mainloop()


# --- GUI Setup ---
dashboard = tk.Tk()
dashboard.update_idletasks()
width = 500
height = 450
x = (dashboard.winfo_screenwidth() // 2) - (width // 2)
y = (dashboard.winfo_screenheight() // 2) - (height // 2)
dashboard.geometry(f"{width}x{height}+{x}+{y}")
dashboard.title("User Dashboard")
dashboard.configure(bg="#1e1e2f")
dashboard.resizable(False, False)

user_id = load_current_user()
user_data = load_user_profile(user_id)

if not user_data:
    tk.Label(dashboard, text="No user data found!", fg="red", bg="#1e1e2f").pack(pady=20)
else:
    tk.Label(dashboard, text="Welcome!", font=("Arial", 24, "bold"), bg="#1e1e2f", fg="white").pack(pady=10)

    tk.Label(dashboard, text=f"User ID: {user_id}", bg="#1e1e2f", fg="white", font=("Arial", 16)).pack()
    tk.Label(dashboard, text=f"Name: {user_data.get('name')}", bg="#1e1e2f", fg="white", font=("Arial", 16)).pack()
    tk.Label(dashboard, text=f"Email: {user_data.get('email')}", bg="#1e1e2f", fg="white", font=("Arial", 16)).pack()
    tk.Label(dashboard, text=f"Phone: {user_data.get('phone')}", bg="#1e1e2f", fg="white", font=("Arial", 16)).pack()
    tk.Label(dashboard, text=f"Adjusting Seat to {user_data.get('seat_position')}", bg="#1e1e2f", fg="white", font=("Arial", 16)).pack()
    tk.Label(dashboard, text=f"Setting AC temperature {user_data.get('ac_temp')} °C", bg="#1e1e2f", fg="white", font=("Arial", 16)).pack()
    tk.Label(dashboard, text=f"Starting Playlist: {user_data.get('playlist')}", bg="#1e1e2f", fg="white", font=("Arial", 16)).pack()


    tk.Label(dashboard, text="", bg="#1e1e2f").pack()  # spacing



# --- Buttons ---
button_style = {
    "width": 20,
    "height": 2,
    "bg": "#33334d",
    "fg": "white",
    "font": ("Helvetica", 10, "bold"),
    "activebackground": "#44445c",
    "relief": "raised",
    "bd": 3,
    "cursor": "hand2"
}

button_frame = tk.Frame(dashboard, bg="#1e1e2f")
button_frame.pack(pady=10)

btn_add = tk.Button(button_frame, text="Add User", command=add_user, **button_style)
btn_delete = tk.Button(button_frame, text="Delete User", command=delete_user, **button_style)
btn_access_logs = tk.Button(button_frame, text="Access Logs", command=view_access_logs, **button_style)
btn_unknown_logs = tk.Button(button_frame, text="Unknown Logs", command=view_unknown_logs, **button_style)

btn_add.grid(row=0, column=0, padx=10, pady=5)
btn_delete.grid(row=0, column=1, padx=10, pady=5)
btn_access_logs.grid(row=1, column=0, padx=10, pady=5)
btn_unknown_logs.grid(row=1, column=1, padx=10, pady=5)


# --- Start GUI ---
dashboard.mainloop()

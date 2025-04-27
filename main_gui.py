import tkinter as tk
from tkinter import simpledialog, messagebox, Menu
from PIL import Image, ImageTk
import subprocess
import os

# ---------------- Password Handling ------------------
def get_stored_password():
    with open("password.txt", "r") as f:
        return f.read().strip()

def change_password():
    current = simpledialog.askstring("Verify", "Enter current password:", show="*")
    if current != get_stored_password():
        messagebox.showerror("Access Denied", "Incorrect password.")
        return

    new_pass = simpledialog.askstring("New Password", "Enter new password:", show="*")
    if not new_pass:
        return
    confirm_pass = simpledialog.askstring("Confirm Password", "Re-enter new password:", show="*")
    if new_pass == confirm_pass:
        with open("password.txt", "w") as f:
            f.write(new_pass)
        messagebox.showinfo("Success", "Password changed successfully.")
    else:
        messagebox.showerror("Mismatch", "Passwords do not match.")

# ---------------- Launcher Logic ------------------
def launch_face():
    launch_button.config(relief="sunken")
    root.after(100, lambda: launch_button.config(relief="flat"))
    subprocess.Popen(["python", "face.py"])
    root.after(200, root.destroy)

def run_setup_script():
    subprocess.Popen(["python", "setup.py"])

def verify_and_launch_dashboard():
    password = simpledialog.askstring("Authentication", "Enter Admin Password:", show="*")
    if password == get_stored_password():
        subprocess.Popen(["python", "dashboard.py"])
        root.destroy()
    else:
        messagebox.showerror("Access Denied", "Incorrect password.")

# ---------------- GUI Setup ------------------
root = tk.Tk()
root.title("Face Recognition Launcher")

# Set size and center
window_width = 500
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
root.configure(bg="#1e1e2f")
root.resizable(False, False)

# Ensure password file exists
if not os.path.exists("password.txt"):
    with open("password.txt", "w") as f:
        f.write("admin123")

# ---------------- Menu Bar ------------------
menu_bar = Menu(root, tearoff=0)

options_menu = Menu(menu_bar, tearoff=0, bg="#2c2c3a", fg="white")
options_menu.add_command(label="Change Password", command=change_password)


menu_bar.add_cascade(label="Options", menu=options_menu)
root.config(menu=menu_bar)

# ---------------- Main Image Button ------------------
image_path = "assets/button_image.png"
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image file '{image_path}' not found.")

img = Image.open(image_path)
img = img.resize((150, 150), Image.Resampling.LANCZOS)
button_image = ImageTk.PhotoImage(img)

container = tk.Frame(root, bg="#1e1e2f")
container.pack(expand=True)

launch_button = tk.Button(
    container,
    image=button_image,
    command=launch_face,
    borderwidth=0,
    relief="flat",
    bg="#1e1e2f",
    activebackground="#2e2e3e",
    highlightthickness=0
)
launch_button.pack()

# ---------------- Bottom Buttons ------------------
bottom_frame = tk.Frame(root, bg="#1e1e2f")
bottom_frame.pack(side="bottom", fill="x", pady=10)

dashboard_button = tk.Button(
    bottom_frame,
    text="Main User",
    command=verify_and_launch_dashboard,
    bg="#33334d",
    fg="white",
    font=("Helvetica", 10, "bold"),
    activebackground="#44445c",
    relief="raised",
    bd=3,
    padx=10,
    pady=5
)
dashboard_button.pack(side="right", padx=(0, 10))

setup_button = tk.Button(
    bottom_frame,
    text="Setup",
    command=run_setup_script,
    bg="#33334d",
    fg="white",
    font=("Helvetica", 10, "bold"),
    activebackground="#44445c",
    relief="raised",
    bd=3,
    padx=10,
    pady=5
)
setup_button.pack(side="right", padx=(0, 10))

# ---------------- Launch App ------------------
root.mainloop()

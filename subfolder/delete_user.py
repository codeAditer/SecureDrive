import os
import shutil
import json
import pickle
import tkinter as tk
from tkinter import messagebox

def delete_user():
    user_id = entry_id.get().strip()

    if not user_id:
        messagebox.showerror("Error", "Please enter a user ID.")
        return

    deleted_any = False

    # 1. Delete dataset folder
    dataset_path = f"dataset/{user_id}"
    if os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)
        deleted_any = True

    # 2. Remove from user_profiles.json
    profile_file = "user_profiles.json"
    if os.path.exists(profile_file):
        with open(profile_file, "r") as f:
            profiles = json.load(f)

        if user_id in profiles:
            del profiles[user_id]
            with open(profile_file, "w") as f:
                json.dump(profiles, f, indent=4)
            deleted_any = True

    # 3. Remove from face_embeddings.pkl
    embeddings_file = "face_embeddings.pkl"
    if os.path.exists(embeddings_file):
        with open(embeddings_file, "rb") as f:
            embeddings = pickle.load(f)

        if user_id in embeddings:
            del embeddings[user_id]
            with open(embeddings_file, "wb") as f:
                pickle.dump(embeddings, f)
            deleted_any = True

    if deleted_any:
        messagebox.showinfo("Success", f"User '{user_id}' successfully deleted.")
        root.destroy() 
    else:
        messagebox.showwarning("Not Found", f"No data found for user ID: {user_id}.")

# GUI setup
root = tk.Tk()
root.title("Delete User")
root.geometry("350x200")

tk.Label(root, text="Enter User ID to Delete").pack(pady=10)
entry_id = tk.Entry(root, width=30)
entry_id.pack(pady=5)

tk.Button(root, text="Delete User", command=delete_user, bg="red", fg="white").pack(pady=20)

root.mainloop()

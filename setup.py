# setup_project_structure.py
import os
import json
import pickle

def setup_project_structure():
    # Required folders
    folders = [
        "dataset",           # Stores user face image datasets
        "unknown_faces",     # Captured unknown face images
        "user_logins",       # Stores user login logs
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"[INIT] Folder created or exists: {folder}")

    # Required files
    files_json = {
        "user_profiles.json": {},
        "current_user.json": {}
    }

    files_pickle = {
        "face_embeddings.pkl": {}  # Default empty dict
    }

    # Create JSON files if not exist
    for filename, default_data in files_json.items():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump(default_data, f, indent=4)
            print(f"[INIT] Created empty JSON file: {filename}")
        else:
            print(f"[INIT] JSON file exists: {filename}")

    # Create Pickle files if not exist
    for filename, default_data in files_pickle.items():
        if not os.path.exists(filename):
            with open(filename, "wb") as f:
                pickle.dump(default_data, f)
            print(f"[INIT] Created empty Pickle file: {filename}")
        else:
            print(f"[INIT] Pickle file exists: {filename}")

    print("[SUCCESS] Project setup complete.")

# Run setup when script is executed directly
if __name__ == "__main__":
    setup_project_structure()

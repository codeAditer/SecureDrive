import cv2
import mediapipe as mp
import time
import pygame
import threading
from scipy.spatial import distance

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

# Eye landmarks
LEFT_EYE = [33, 133]  # corners
RIGHT_EYE = [362, 263]  # corners

# Use multiple points for vertical measurement (averaged)
LEFT_EYE_TOP = [159, 160]
LEFT_EYE_BOTTOM = [145, 144]

RIGHT_EYE_TOP = [386, 385]
RIGHT_EYE_BOTTOM = [374, 380]

# Constants
EAR_THRESHOLD = 0.25
EYE_CLOSED_DURATION = 3  # seconds
HEAD_TURN_DURATION = 3   # seconds
ALERT_COOLDOWN = 2       # prevent spam alerts
ALERT_MESSAGE_TIMEOUT = 3  # seconds to keep the message displayed

# Initialize Pygame mixer
pygame.mixer.init()

# Sound file path
sound_path = "assets/beep.mp3"

# Function to play alert sound
def play_alert():
    try:
        alert_sound = pygame.mixer.Sound(sound_path)
        alert_sound.play()
    except pygame.error as e:
        print(f"Error playing sound: {e}")

# EAR with averaged top/bottom landmarks
def get_ear(landmarks, corners, top_ids, bottom_ids, w, h):
    def avg_y(indices):
        return sum(landmarks[i].y for i in indices) / len(indices)
    
    left = landmarks[corners[0]]
    right = landmarks[corners[1]]

    top_avg = avg_y(top_ids)
    bottom_avg = avg_y(bottom_ids)

    vertical_dist = abs(top_avg - bottom_avg) * h
    horizontal_dist = abs(left.x - right.x) * w

    return vertical_dist / horizontal_dist

# State variables
eye_closed_start = None
head_turn_start = None
last_alert_time = 0
alert_message = ""  # Variable to hold the message to be displayed
alert_time = 0

# Start video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    if result.multi_face_landmarks:
        landmarks = result.multi_face_landmarks[0].landmark

        current_time = time.time()

        # EAR calculation
        left_ear = get_ear(landmarks, LEFT_EYE, LEFT_EYE_TOP, LEFT_EYE_BOTTOM, w, h)
        right_ear = get_ear(landmarks, RIGHT_EYE, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM, w, h)
        avg_ear = (left_ear + right_ear) / 2.0

        # Eye closure detection
        if avg_ear < EAR_THRESHOLD:
            if eye_closed_start is None:
                eye_closed_start = current_time
            elif current_time - eye_closed_start >= EYE_CLOSED_DURATION:
                if current_time - last_alert_time > ALERT_COOLDOWN:
                    threading.Thread(target=play_alert).start()
                    last_alert_time = current_time
                    alert_message = "WARNING: EYE CLOSURE DETECTED!"
                    alert_time = current_time
                eye_closed_start = None
        else:
            eye_closed_start = None

        # Head orientation detection
        nose_x = landmarks[1].x
        if nose_x < 0.4 or nose_x > 0.6:
            if head_turn_start is None:
                head_turn_start = current_time
            elif current_time - head_turn_start >= HEAD_TURN_DURATION:
                if current_time - last_alert_time > ALERT_COOLDOWN:
                    threading.Thread(target=play_alert).start()
                    last_alert_time = current_time
                    alert_message = "WARNING: HEAD TURN DETECTED!"
                    alert_time = current_time
                head_turn_start = None
        else:
            head_turn_start = None
    
    # Remove the alert message after the timeout duration (3 seconds)
    if current_time - alert_time >= ALERT_MESSAGE_TIMEOUT:
        alert_message = ""  # Clear the alert message after 3 seconds

    # Overlay the alert message on the frame
    if alert_message:
        cv2.putText(frame, alert_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow("Driver Monitor", frame)
    
    # Exit the loop when 'ESC' is pressed
    if cv2.waitKey(1) & 0xFF == 27:  
        break

# Release resources after the loop
cap.release()
cv2.destroyAllWindows()

import cv2
import csv
import os
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# -- MediaPipe setup --
# Aliases
BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"), # Location to store model
    running_mode=VisionRunningMode.VIDEO, # Video mode
    num_hands=1 # Only detect one hand for now
)
# Create detector object
landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0) # Start webcam (default webcam)
frame_id = 0 # MediaPipe needs each frame to have a unique increasing timestamp

# -- Dataset storage (dynamic appending) --

filename = "LH_dataset.csv"

# create file if it doesn't exist
if not os.path.exists(filename):
    open(filename, "w").close()
# dictionary for ease of organization
label_map = {
    'd': (0, "DO"),
    'r': (1, "RE"),
    'm': (2, "MI"),
    'f': (3, "FA"),
    's': (4, "SO"),
    'l': (5, "LA"),
    't': (6, "TI"),
}

# counters for each class
counts = {name: 0 for _, name in label_map.values()}


# Instructions
print("\nControls:")
print("d r m f s l t → solfege labels")
print("  q = quit/finish\n")


# -- Main loop --

while True:
    ret, frame = cap.read() # Read a frame from webcam
    frame = cv2.flip(frame, 1)   # mirror frame
    if not ret:
        break
    # Convert frame to MediaPipe image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    # Run hand detection
    # detect_for_video() takes image and timestamp, and returns landmarks for each detected hand
    result = landmarker.detect_for_video(mp_image, frame_id)
    frame_id += 1

    features = None

    if result.hand_landmarks:

        hand = result.hand_landmarks[0]

        features = []

        for lm in hand: # (each hand has 21 landmarks (x,y,z))
            # Save x,y,z for each landmark
            features += [lm.x, lm.y, lm.z]

            # Dispaly circles on monitor
            h, w, _ = frame.shape
            # Convert normalized coords to pixel coords
            x = int(lm.x * w)
            y = int(lm.y * h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1) # Draw marker
    
    # Show the frame with counters of samples
    y_pos = 30
    total = sum(counts.values())

    for name in counts:
        cv2.putText(frame, f"{name}: {counts[name]}",
                    (20, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0), 2)
        y_pos += 25

    cv2.putText(frame, f"TOTAL: {total}",
                (20, y_pos + 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 0), 2)

    cv2.imshow("Left Hand Data Collector", frame)

    key = cv2.waitKey(1) & 0xFF # only get last byte of key value (just in case)

    # Only save if a hand is detected
    if features:
        key_char = chr(key) if key != 255 else None # convert ASCII to char, and if no key, do nothing

        if key_char in label_map:
            label, name = label_map[key_char]

            with open(filename, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(features + [label])

            counts[name] += 1
            print(f"Labelled as {name}")

    if key == ord('q'):
        break

# -- Cleanup --

cap.release()
cv2.destroyAllWindows()

print(f"\nFinished.")

for k, v in counts.items():
    print(f"{k}: {v}")

print("TOTAL:", sum(counts.values()))
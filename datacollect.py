import cv2
import csv
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
    num_hands=2 # Only detect one hand for now
)
# Create detector object
landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0) # Start webcam
frame_id = 0 # MediaPipe needs each frame to have a unique increasing timestamp

# -- Dataset storage --

data = []

# Instructions
print("\nControls:")
print("  o = label OPEN")
print("  c = label CLOSED")
print("  q = quit\n")


# -- Main loop --

while True:

    ret, frame = cap.read() # Read a frame from webcam
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


    cv2.imshow("Data Collector", frame) # Show the frame

    key = cv2.waitKey(1) & 0xFF # Escape method is esc key

    # Only save if a hand is detected
    if features:
        if key == ord('o'):
            data.append(features + [0])
            print("labelled as OPEN")

        if key == ord('c'):
            data.append(features + [1])
            print("labelled as CLOSED")

    if key == ord('q'):
        break

# -- Save CSV --

with open("hands_dataset.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

print(f"\nSaved {len(data)} samples to hands_dataset.csv")

cap.release()
cv2.destroyAllWindows()
import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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

    # Display landmarks on screen
    if result.hand_landmarks:
        # For each detected hand
        for hand in result.hand_landmarks:
            for lm in hand: # (each hand has 21 landmarks (x,y,z))
                h, w, _ = frame.shape
                # Convert normalized coords to pixel coords
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1) # Draw marker

    cv2.imshow("Hand Tracker", frame) # Show the frame

    if cv2.waitKey(1) & 0xFF == 27: # Exit Hand Tracker on esc key
        break

# Close window
cap.release()
cv2.destroyAllWindows()
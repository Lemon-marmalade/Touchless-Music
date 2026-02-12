
import torch
import torch.nn as nn

import cv2
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

# Definition of NN
class HandNet(nn.Module):
    def __init__(self, num_classes):
        super().__init__() # inherit all of nn.Module __init__
        # Layers
        self.net = nn.Sequential(
            nn.Linear(63, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.net(x)

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

        # Recognize hand position
        model = HandNet(2) # 2 possible labels
        model.load_state_dict(torch.load("RH_model.pt"))
        model.eval()

        with torch.no_grad():
            features = torch.tensor(features, dtype=torch.float32)
            pred = model(features)
            label = pred.argmax().item()

        cv2.putText(frame, f"Hand is: {label}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.imshow("Right Hand Predict", frame)

    key = cv2.waitKey(1) & 0xFF # only get last byte of key value (just in case)
    if key == ord('q'):
        break

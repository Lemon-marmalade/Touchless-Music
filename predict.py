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
    num_hands=2 # Detect 2 hands
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
# -- Load models --
modell = HandNet(7)
modell.load_state_dict(torch.load("LH_model2.pt"))
modell.eval()

modelr = HandNet(2)
modelr.load_state_dict(torch.load("RH_model.pt"))
modelr.eval()
# -- Main Loop --
while True:

    ret, frame = cap.read() # Read a frame from webcam

    if not ret:
        break
    frame = cv2.flip(frame, 1)   # must fip first, because that's how my model was trained
    # Convert frame to MediaPipe image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    # Run hand detection
    # detect_for_video() takes image and timestamp, and returns landmarks for each detected hand
    result = landmarker.detect_for_video(mp_image, frame_id)
    frame_id += 1


    featuresr = featuresl = None

    if result.hand_landmarks:

        for i, hand_landmarks in enumerate(result.hand_landmarks):

            handedness = result.handedness[i][0].category_name  # Returns "Left" or "Right"... but because screen is mirrored, is actually reverse
            features = []

            for lm in hand_landmarks:
                features += [lm.x, lm.y, lm.z]

                h, w, _ = frame.shape
                x = int(lm.x * w)
                y = int(lm.y * h)

                if handedness == "Right": # opposite since display is mirrored
                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1) # Huh... color format is bgr
                else:
                    cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

            if handedness == "Right": # opposite since display is mirrored
                featuresl = features
            else:
                featuresr = features

    # LEFT HAND
    if featuresl is not None:
        featuresl = torch.tensor(featuresl, dtype=torch.float32)

        with torch.no_grad():
            predl = modell(featuresl)
            labell = predl.argmax().item()

        gesturel = ["DO", "RE", "MI", "FA", "SO", "LA", "TI"]
        cv2.putText(frame, f"Left Hand: {gesturel[labell]}",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0,255,0), 2)


    # RIGHT HAND
    if featuresr is not None:
        featuresr = torch.tensor(featuresr, dtype=torch.float32)

        with torch.no_grad():
            predr = modelr(featuresr)
            labelr = predr.argmax().item()

        gesturer = ["OPEN", "CLOSED"]
        cv2.putText(frame, f"Right Hand: {gesturer[labelr]}",
                    (1680, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0,255,255), 2)
    
    cv2.imshow("Hand Prediction", frame)

    key = cv2.waitKey(1) & 0xFF # only get last byte of key value (just in case)
    if key == ord('q'):
        break

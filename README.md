# Touchless Music

Touchless Music is a hand-tracked musical instrument that leans fully into the ridiculous in the best possible way: part touchless otamatone, part solfege conductor, part computer vision experiment.

The core idea is split across two hands:

- One hand controls whether the instrument "sings" at all by making an open or closed sock-puppet shape.
- That same voice gets its pitch from distance to an ultrasonic sensor, creating a touchless slide instrument.
- The other hand performs solfege gestures (`Do Re Mi Fa So La Ti`) that trigger a second harmonizing voice.

While it's impractical, overengineered, and deeply committed to making music in a way no one asked for, this has been a fun side project, and that's sort of the whole essence I was going for :)

## What This Repo Contains

This repository includes the computer-vision pipeline, trained models, Arduino sketches, datasets, and hardware files used to build the instrument.

### Python / ML

- `predict.py`: main runtime script. Detects both hands with MediaPipe, classifies gestures with PyTorch, and sends the results to Arduino over serial.
- `collect_r.py`: collects right-hand training data for `OPEN` vs `CLOSED`.
- `collect_l.py`: collects left-hand training data for `DO RE MI FA SO LA TI`.
- `train.py`: trains a feedforward classifier from CSV landmark data.
- `RH_predict.py`: tests the right-hand gesture model by itself.
- `LH_predict.py`: tests the left-hand gesture model by itself.
- `test.py`: visual hand-tracking sanity check with MediaPipe landmarks only.

### Models and data

- `hand_landmarker.task`: MediaPipe hand landmark model asset.
- `RH_dataset.csv`: right-hand training samples.
- `LH_dataset2.csv`: left-hand training samples.
- `RH_model.pt`: trained right-hand classifier.
- `LH_model2.pt`: trained left-hand classifier.
- `hands_dataset(test).csv`: additional dataset artifact.

### Arduino

- `Touchless_Music_Arduino_Code/Touchless_Music_Arduino_Code.ino`: full two-voice system. One buzzer is pitch-controlled by ultrasonic distance, the second buzzer is driven by solfege gesture labels from the left hand.
- `Touchless_Otamatone_original/Touchless_Otamatone_original.ino`: earliest single-voice touchless otamatone prototype.
- `Touchless_Otamatone_button_control/Touchless_Otamatone_button_control.ino`: intermediate version that only plays when a separate speak/button signal is active.

### Hardware and reference files

- `CAD/`: printable enclosure and slider parts.
- `Wiring/`: build photos for the buzzer-only and push-button versions.

## How It Works

At runtime, the webcam feed is processed with MediaPipe Hands. For each detected hand, the 21 landmark positions are flattened into 63 values (`x, y, z` for every joint) and passed into a small neural network.

The repo currently uses two separate classifiers:

- Right hand: `OPEN` or `CLOSED`
- Left hand: `DO RE MI FA SO LA TI`

`predict.py` sends both predictions to Arduino as a serial message:

```text
<right-hand-label> <left-hand-label>
```

The Arduino sketch then does two things:

- If the right hand is `OPEN`, it reads the ultrasonic sensor and maps hand distance to a chromatic pitch.
- If the left hand is recognized as a solfege sign, it plays a harmonizing note on a second buzzer.

## Setup

### 1. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Connect hardware

The full version expects:

- a webcam
- an Arduino-compatible board
- an ultrasonic distance sensor
- two buzzers/speakers

Wiring reference photos are in `Wiring/`, and the full sketch lives in `Touchless_Music_Arduino_Code/`.

### 3. Check Arduino dependencies

The Arduino sketches include `pitches.h`, but that header is not currently committed in this repo. You will need to add it to the Arduino sketch folder or your Arduino project before uploading.

### 4. Set the serial port

`predict.py` currently hard-codes:

```python
SERIAL_PORT = "/dev/cu.usbmodem101"
```

Change that value to match your machine before running the full system.

## Running the Project

### Quick webcam sanity check

```bash
python test.py
```

This only verifies MediaPipe hand tracking.

### Test each classifier independently

```bash
python RH_predict.py
python LH_predict.py
```

### Run the full instrument

1. Upload `Touchless_Music_Arduino_Code/Touchless_Music_Arduino_Code.ino` to the board.
2. Confirm the serial port in `predict.py`.
3. Run:

```bash
python predict.py
```

Press `q` to quit the OpenCV window.

## Collecting More Training Data

To record additional gesture samples:

```bash
python collect_r.py
python collect_l.py
```

Controls:

- `collect_r.py`: `o` = open, `c` = closed, `q` = quit
- `collect_l.py`: `d r m f s l t` = `Do Re Mi Fa So La Ti`, `q` = quit

Each captured frame stores MediaPipe landmarks plus a label into the corresponding CSV file.

## Retraining

The current `train.py` is configured for the left-hand 7-class model:

```bash
python train.py
```

If you want to retrain the right-hand model, update the dataset path and output class count in `train.py` first.

## Repo Notes

- The models were trained on mirrored webcam input, so several scripts flip the frame before inference.
- In `predict.py`, MediaPipe handedness is intentionally interpreted in reverse because the display is mirrored.
- The current setup is tuned for local experimentation rather than polished deployment.

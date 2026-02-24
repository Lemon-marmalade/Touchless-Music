#include "pitches.h"

#define BUZZER1 12
#define ECHO 11
#define TRIG 10
#define BUZZER2 9

// chromatic scale
int scale1[] = {NOTE_C5, NOTE_CS5, NOTE_D5, NOTE_DS5, NOTE_E5, NOTE_F5, NOTE_FS5, NOTE_G5, NOTE_GS5, NOTE_A5, NOTE_AS5, NOTE_B5, NOTE_C6};
int scale2[] = {NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4};

int idx, lastIdx;

void setup() {
  Serial.begin(9600);
  pinMode(ECHO, INPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(BUZZER1, OUTPUT);
  pinMode(BUZZER2, OUTPUT);
}

void loop() {
  int newR = -1, newL = -1; // Initialize to impossible values
  if (Serial.available()) {
        newR = Serial.parseFloat();
        newL = Serial.parseFloat();
  }
  // -- Right Hand Logic --
  if (newR==0) // label for open RH is 0
  {
    // Send ultrasonic pulse
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH); // 10 us pulse
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    long echo = pulseIn(ECHO, HIGH, 60000); // timeout: wait 60ms (best sounding). if no echo, do nothing
    if (echo == 0) {
      // no echo keep previous note, don't retrigger
      tone(BUZZER1, scale1[lastIdx]);
      return;
    }
    float distance = echo * 0.034 / 2;   // cm

    // clamp distance to 0–25 cm range
    distance = constrain(distance, 0, 25);

    // divide into 8 buckets (for the 13 notes) across 1–25 cm 
    // (lower bound is higher as an offset of sensor imperfections)
    idx = map(distance, 2, 25, 0, 12);

    // only change tone when distance changes
    if (idx != lastIdx)
    {
      tone(BUZZER1, scale1[idx]); 
      lastIdx = idx;
    }
  }
  else
  {
    noTone(BUZZER1);
  }
  // -- Left Hand Logic --
  if (newL != -1) // If left hand gesture was able to be recognized
  {
    tone(BUZZER1, scale2[newL]); 
  }
  else
  {
    noTone(BUZZER1);
  }

}
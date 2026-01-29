#include "pitches.h"

#define TRIG 10
#define ECHO 11
#define BUZZER 8

// chromatic scale
int scale[] = {NOTE_C5, NOTE_CS5, NOTE_D5, NOTE_DS5, NOTE_E5, NOTE_F5, NOTE_FS5, NOTE_G5, NOTE_GS5, NOTE_A5, NOTE_AS5, NOTE_B5, NOTE_C6};

int lastIdx = -1;

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(BUZZER, OUTPUT);
}

void loop() {

  // Send ultrasonic pulse
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); // 10 us pulse
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long echo = pulseIn(ECHO, HIGH, 50000); // timeout: wait 30ms, if no echo, return
   if (echo == 0) {
    // no echo keep current note, don't retrigger
    return;
  }
  float distance = echo * 0.034 / 2;   // cm

  // clamp distance to 0–25 cm range
  distance = constrain(distance, 0, 25);

  // divide into 8 buckets (for the 13 notes) across 0–25 cm
  int idx = map(distance, 0, 25, 0, 12);

  idx = constrain(idx, 0, 12);

  // only change tone when note changes
  if (idx != lastIdx) {
    tone(BUZZER, scale[idx]);
    lastIdx = idx;
  }
}

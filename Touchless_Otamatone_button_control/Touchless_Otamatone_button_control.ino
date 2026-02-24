#include "pitches.h"

#define ECHO 11
#define TRIG 10
#define SPEAK 9
#define BUZZER 8

// chromatic scale
int scale[] = {NOTE_C5, NOTE_CS5, NOTE_D5, NOTE_DS5, NOTE_E5, NOTE_F5, NOTE_FS5, NOTE_G5, NOTE_GS5, NOTE_A5, NOTE_AS5, NOTE_B5, NOTE_C6};

int idx, lastIdx;

void setup() {
  //Serial.begin(9600); // for debugging
  pinMode(ECHO, INPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(SPEAK, INPUT);
  pinMode(BUZZER, OUTPUT);
}

void loop() {
  if (digitalRead(SPEAK)==HIGH) // only make sound when speak signal is high
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
      tone(BUZZER, scale[lastIdx]);
      return;
    }
    float distance = echo * 0.034 / 2;   // cm

    // clamp distance to 0–25 cm range
    distance = constrain(distance, 0, 25);

    // divide into 8 buckets (for the 13 notes) across 1–25 cm 
    // (lower bound is higher as an offset of sensor imperfections)
    idx = map(distance, 2, 25, 0, 12);

    //idx = constrain(idx, 0, 12); // redundant...?

    // only change tone when distance changes
    if (idx != lastIdx) {
      tone(BUZZER, scale[idx]); 
      lastIdx = idx;
    }
  }
  else
  {
    noTone(BUZZER);
  }
}

#include "pitches.h"
#include <TimerOne.h>

#define BUZZER1 12  // will be driven by Timer1
#define ECHO 11
#define TRIG 10
#define BUZZER2 9   // will use tone()
// chromatic scale (RH)
int scale1[] = {NOTE_C5, NOTE_CS5, NOTE_D5, NOTE_DS5, NOTE_E5, NOTE_F5, NOTE_FS5, NOTE_G5, NOTE_GS5, NOTE_A5, NOTE_AS5, NOTE_B5, NOTE_C6};
// diatonic scale (LH)
int scale2[] = {NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4};

volatile bool buzzer1_state = false; // off
volatile int buzzer1_freq = 0; // off

// Toggle BUZZER1 on Timer1 interrupt
void toggleBuzzer1() 
{
  buzzer1_state = !buzzer1_state;
  digitalWrite(BUZZER1, buzzer1_state? HIGH : LOW);
}

// Start the Timer1-based tone for BUZZER1 at freq Hz
void startBuzzer1(int freq) 
{
  if (freq <= 0) 
  {
    Timer1.detachInterrupt(); // TIMSK1 = 0
    digitalWrite(BUZZER1, LOW);
    buzzer1_freq = 0;
    return;
  }
  // half period in microseconds = 500000 / freq
  long half_us = 500000 / freq; // upper bound for timer
  Timer1.initialize(half_us);
  Timer1.attachInterrupt(toggleBuzzer1);
  buzzer1_freq = freq;
}

// Stop buzzer1
void stopBuzzer1() 
{
  startBuzzer1(0);
}

int idx = -1, lastIdx = -1;

void setup() 
{
  Serial.begin(115200);
  pinMode(ECHO, INPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(BUZZER1, OUTPUT); // RH: Timer1
  pinMode(BUZZER2, OUTPUT); // LH: tone()

  // For added precaution, make sure both buzzers are off to start
  noTone(BUZZER1);
  noTone(BUZZER2);
  digitalWrite(BUZZER1, LOW);
  digitalWrite(BUZZER2, LOW);

  // Ensure Timer1 is not running yet:
  Timer1.detachInterrupt();
}

void loop() {
  int newR = -1, newL = -1;
  if (Serial.available() >= 1) 
  {
    newR = Serial.parseFloat();
    newL = Serial.parseFloat();
  }

  // -- Right Hand (ultrasonic) --
  if (newR == 0) 
  {
    // Send ultrasonic pulse
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    long echo = pulseIn(ECHO, HIGH, 60000); // 60 ms timeout

    if (echo==0)
    {
      // no echo keep previous note, don't retrigger
      startBuzzer1(scale1[idx]);
      return;
    }
    else
    {
      float distance = echo * 0.034 / 2.0; // cm

      // clamp distance to 0–25 cm range
      distance = constrain(distance, 0, 25);

      // divide into 8 buckets (for the 13 notes) across 1–25 cm 
      // (lower bound is higher as an offset of sensor imperfections)
      idx = map(distance, 2, 25, 0, 12);

      // only change tone when distance changes
      if (idx != lastIdx) 
      {
        startBuzzer1(scale1[idx]);
        lastIdx = idx;
      }
    }
  } else // RH not open
  {
    stopBuzzer1();
  }

  // -- Left Hand (gesture -> scale2) --
  if (newL >= 0 && newL <= 6) // If left hand gesture was able to be recognized
  {
    tone(BUZZER2, scale2[newL]);
  } else {
    noTone(BUZZER2);
  }
  delay(10); // small debounce
}
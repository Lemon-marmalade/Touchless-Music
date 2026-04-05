#include "pitches.h"

#define BUZZER1 9   // Timer1 OC1A (D9)
#define ECHO 11
#define TRIG 10
#define BUZZER2 3   // Timer2 OC2B (D3)

int scale1[] = {NOTE_C5, NOTE_CS5, NOTE_D5, NOTE_DS5, NOTE_E5, NOTE_F5, NOTE_FS5, NOTE_G5, NOTE_GS5, NOTE_A5, NOTE_AS5, NOTE_B5, NOTE_C6};
int scale2[] = {NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_G4, NOTE_A4, NOTE_B4};

// Timer1 prescaler = 8: OCR1A = 16000000 / (2 * 8 * freq) - 1
const uint16_t scale1_ocr[13] = 
{
  1912, 1805, 1703, 1607, 1517, 1432, 1351,
  1275, 1203, 1135, 1071, 1011, 955
};

// Timer2 prescaler = 256: OCR2A = OCR2B = 16000000 / (2 * 256 * freq) - 1
const uint8_t scale2_ocr[7] = 
{
  119,  // C4  261.63 Hz
  106,  // D4  293.66 Hz
  94,   // E4  329.63 Hz
  89,   // F4  349.23 Hz
  79,   // G4  392.00 Hz
  70,   // A4  440.00 Hz
  63    // B4  493.88 Hz
};

void setupTimers() 
{
  // Timer1: * need full register writes instead of bit fiddling to account for bits changed by Arduino bootloader
  TCCR1A = 0;
  TCCR1B = 0;
  TCCR1A = (1 << COM1A0); // toggle OC1A, disconnected until note starts
  TCCR1B = (1 << WGM12) | (1 << CS11); // CTC, prescaler 8

  // Timer2: full register writes
  TCCR2A = 0;
  TCCR2B = 0;
  TCCR2A = (1 << WGM21); // CTC, OC2B disconnected until note starts
  TCCR2B = (1 << CS22) | (1 << CS21); // prescaler 256
}

void startBuzzer1_idx(int noteIdx) 
{
  if (noteIdx < 0 || noteIdx >= 13) 
  {
    TCCR1A = (1 << COM1A0);  // keep toggle mode but disconnected? 
    // actually just clear COM1A0 to disconnect
    TCCR1A = 0;
    digitalWrite(BUZZER1, LOW);
    return;
  }
  OCR1A  = scale1_ocr[noteIdx];
  TCCR1A = (1 << COM1A0);   // connect OC1A toggle
}

void stopBuzzer1() 
{
  TCCR1A = 0;               // disconnect OC1A
  digitalWrite(BUZZER1, LOW);
}

void startBuzzer2_idx(int noteIdx) 
{
  if (noteIdx < 0 || noteIdx >= 7) 
  {
    TCCR2A = (1 << WGM21);  // keep CTC but disconnect OC2B
    digitalWrite(BUZZER2, LOW);
    return;
  }
  TCNT2  = 0;
  OCR2A  = scale2_ocr[noteIdx];
  OCR2B  = scale2_ocr[noteIdx];
  TCCR2A = (1 << COM2B0) | (1 << WGM21);  // connect OC2B toggle, CTC
}

void stopBuzzer2() 
{
  TCCR2A = (1 << WGM21);   // keep CTC but disconnect OC2B
  digitalWrite(BUZZER2, LOW);
}

int idx = -1, lastIdx = -1;

void setup() 
{
  Serial.begin(115200);
  pinMode(ECHO, INPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(BUZZER1, OUTPUT);
  pinMode(BUZZER2, OUTPUT);

  digitalWrite(BUZZER1, LOW);
  digitalWrite(BUZZER2, LOW);

  setupTimers();
}

void loop() 
{
  int newR = -1, newL = -1;
  if (Serial.available() >= 1) 
  {
    newR = Serial.parseFloat();
    newL = Serial.parseFloat();
  }

  // -- Right Hand (ultrasonic) --
  if (newR == 0) {
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    long echo = pulseIn(ECHO, HIGH, 60000);

    if (echo == 0) {
      return; // no echo, keep last note playing
    } 
    else 
    {
      float distance = echo * 0.034 / 2.0;
      distance = constrain(distance, 0, 25);
      idx = map(distance, 2, 25, 0, 12);

      if (idx != lastIdx) 
      {
        startBuzzer1_idx(idx);
        lastIdx = idx;
      }
    }
  } 
  else 
  {
    stopBuzzer1();
    lastIdx = -1;
  }

  // -- Left Hand (gesture -> scale2) --
  if (newL >= 0 && newL <= 6) 
  {
    startBuzzer2_idx(newL);
  } 
  else 
  {
    stopBuzzer2();
  }

  delay(10);
}
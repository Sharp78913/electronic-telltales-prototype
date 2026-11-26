/*
  Electronic Sail Telltales – HX711 single-gauge prototype
  Board: Arduino Uno (ATmega328P)
  Library: bogde/HX711 (install "HX711" from Arduino IDE Library Manager)

  Serial data: DATA,<sensor_id>,<arduino_millis>,<raw_counts>,<zeroed_counts>
  Commands: ZERO, PING, INFO (each terminated by newline)

  IMPORTANT: counts are NOT volts, strain or wind speed.
  Actual sample rate depends on HX711 board RATE hardware configuration.
*/
#include <Arduino.h>
#include "HX711.h"
#include <string.h>

const uint8_t DATA_PIN = 2;
const uint8_t CLOCK_PIN = 3;
const uint8_t SENSOR_ID = 1;
const unsigned long SERIAL_BAUD = 115200;
const uint8_t BASELINE_SAMPLES = 12;
const unsigned long WARNING_INTERVAL_MS = 2500;

HX711 adc;
long zeroOffset = 0;
long zeroTotal = 0;
uint8_t zeroReadings = 0;
bool zeroInProgress = true;
unsigned long lastDataTime = 0;
unsigned long lastWarningTime = 0;
char commandBuffer[16];
uint8_t commandLength = 0;

void beginZero() {
  zeroTotal = 0;
  zeroReadings = 0;
  zeroInProgress = true;
  Serial.println(F("#EVENT,ZERO_BEGIN"));
}

void handleCommand(const char *cmd) {
  if (strcmp(cmd, "ZERO") == 0) {
    beginZero();
  } else if (strcmp(cmd, "PING") == 0) {
    Serial.println(F("#PONG"));
  } else if (strcmp(cmd, "INFO") == 0) {
    Serial.println(F("#INFO,protocol=1,adc=HX711,sensors=1,baud=115200,units=counts"));
  } else if (cmd[0] != '\0') {
    Serial.println(F("#ERROR,UNKNOWN_COMMAND"));
  }
}

void readCommands() {
  while (Serial.available()) {
    const char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      commandBuffer[commandLength] = '\0';
      handleCommand(commandBuffer);
      commandLength = 0;
    } else if (commandLength < sizeof(commandBuffer) - 1) {
      commandBuffer[commandLength++] = c;
    } else {
      // Discard an overlong command rather than overflowing the buffer.
      commandLength = 0;
      Serial.println(F("#ERROR,COMMAND_TOO_LONG"));
    }
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  adc.begin(DATA_PIN, CLOCK_PIN, 128); // HX711 channel A, gain 128
  Serial.println(F("#INFO,protocol=1,adc=HX711,sensors=1,baud=115200,units=counts"));
  beginZero();
  lastDataTime = millis();
  lastWarningTime = millis();
}

void loop() {
  readCommands();

  // Never wait indefinitely for a disconnected or incorrectly wired ADC.
  if (adc.is_ready()) {
    const long raw = adc.read();
    lastDataTime = millis();

    if (zeroInProgress) {
      zeroTotal += raw;
      ++zeroReadings;
      if (zeroReadings >= BASELINE_SAMPLES) {
        zeroOffset = zeroTotal / (long)BASELINE_SAMPLES;
        zeroInProgress = false;
        Serial.print(F("#EVENT,ZERO_OK,"));
        Serial.println(zeroOffset);
      }
      return;
    }

    Serial.print(F("DATA,"));
    Serial.print(SENSOR_ID);
    Serial.print(',');
    Serial.print(millis());
    Serial.print(',');
    Serial.print(raw);
    Serial.print(',');
    Serial.println(raw - zeroOffset);
  } else {
    const unsigned long now = millis();
    if (now - lastWarningTime >= WARNING_INTERVAL_MS &&
        now - lastDataTime >= WARNING_INTERVAL_MS) {
      Serial.println(F("#WARN,HX711_NOT_READY_CHECK_POWER_AND_WIRING"));
      lastWarningTime = now;
    }
  }
}

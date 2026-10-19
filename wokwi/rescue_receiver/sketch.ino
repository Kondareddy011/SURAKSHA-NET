/*
 * ============================================================================
 * SURAKSHA-NET: Smart Soldier Protection, Survival & Rescue System
 * Component: Tactical Rescue Receiver Gateway (Wokwi Simulation Firmware)
 * Target MCU: ESP32-WROOM-32 / ESP32 DevKit V1
 *
 * SIMULATION BEHAVIOR:
 * - Continuously listens for JSON telemetry packets over Serial (or simulated link).
 * - Updates high-contrast OLED display with latest casualty vital signs & GPS.
 * - Triggers high-intensity red LED strobe and acoustic dual-tone siren on EMERGENCY.
 * - Operator can press green tactile button (GPIO 14) to ACKNOWLEDGE and mute alarm.
 * - Type "EMERGENCY" in Serial Monitor to inject a test casualty packet!
 * - Type "SAFE" to clear alerts and return to baseline monitoring.
 * ============================================================================
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

// Hardware Pinout
#define PIN_SDA            21
#define PIN_SCL            22
#define PIN_LED_EMERGENCY   4  // Red Alert Strobe
#define PIN_LED_NET         2  // Blue Packet Received Pulse
#define PIN_SIREN          15  // Acoustic Siren / Buzzer
#define PIN_BTN_ACK        14  // Operator Acknowledge Tactile Switch

// OLED Specs
#define SCREEN_WIDTH      128
#define SCREEN_HEIGHT      64
#define SCREEN_ADDR      0x3C

Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// State Variables
bool emergencyActive = false;
bool emergencyMuted = false;
unsigned long lastSirenToggle = 0;
bool sirenToneHigh = false;
unsigned long demoTimer = 0;

// Current Monitored Casualty Details
String monSoldierId = "DELTA-LEAD";
String monName = "Sepoy Rajesh Kumar";
String monStatus = "SAFE";
String monAlert = "NOMINAL PATROL";
int monHeartRate = 74;
int monSpO2 = 98;
float monLat = 35.4211;
float monLon = 77.1095;
int monHops = 2;

void updateOled();
void handleAudioVisuals();
void parsePacket(const String& jsonStr);

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(PIN_LED_EMERGENCY, OUTPUT);
  pinMode(PIN_LED_NET, OUTPUT);
  pinMode(PIN_SIREN, OUTPUT);
  pinMode(PIN_BTN_ACK, INPUT_PULLUP);

  digitalWrite(PIN_LED_EMERGENCY, LOW);
  digitalWrite(PIN_LED_NET, LOW);
  digitalWrite(PIN_SIREN, LOW);

  Wire.begin(PIN_SDA, PIN_SCL);

  if (!oled.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDR)) {
    Serial.println(F("[ERROR] SSD1306 OLED initialization failed!"));
  } else {
    oled.clearDisplay();
    oled.setTextColor(SSD1306_WHITE);
    oled.setTextSize(1);
    oled.setCursor(0, 10);
    oled.println(F("SURAKSHA-NET BASE"));
    oled.setCursor(0, 25);
    oled.println(F("Tactical Receiver"));
    oled.setCursor(0, 40);
    oled.println(F("Standby for LoRa..."));
    oled.display();
    delay(1000);
  }

  Serial.println(F("=================================================="));
  Serial.println(F(" SURAKSHA-NET RESCUE RECEIVER BASE STATION"));
  Serial.println(F(" Interactive Wokwi Simulation Ready"));
  Serial.println(F(" Instructions:"));
  Serial.println(F(" - Type 'EMERGENCY' to simulate receiving SOS casualty packet."));
  Serial.println(F(" - Type 'SAFE' to simulate all units nominal."));
  Serial.println(F(" - Press green button (GPIO 14) to ACK/MUTE alarm."));
  Serial.println(F("=================================================="));

  updateOled();
}

void loop() {
  unsigned long now = millis();

  // 1. Check Acknowledge Button
  if (digitalRead(PIN_BTN_ACK) == LOW) {
    if (emergencyActive && !emergencyMuted) {
      emergencyMuted = true;
      Serial.println(F("[OPERATOR ACK] Emergency acknowledged and siren muted."));
      digitalWrite(PIN_SIREN, LOW);
      digitalWrite(PIN_LED_EMERGENCY, HIGH); // Steady ON when ACK'd
      updateOled();
      delay(300); // Debounce
    }
  }

  // 2. Read Serial Input
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.equalsIgnoreCase("EMERGENCY") || input.equalsIgnoreCase("SOS")) {
      digitalWrite(PIN_LED_NET, HIGH);
      emergencyActive = true;
      emergencyMuted = false;
      monStatus = "EMERGENCY";
      monAlert = "MANUAL_SOS / BLAST";
      monHeartRate = 148;
      monSpO2 = 88;
      Serial.println(F("[BASE STATION ALERT] INCOMING CASUALTY BEACON DETECTED!"));
      updateOled();
      delay(50);
      digitalWrite(PIN_LED_NET, LOW);
    } else if (input.equalsIgnoreCase("SAFE") || input.equalsIgnoreCase("RESET")) {
      emergencyActive = false;
      emergencyMuted = false;
      monStatus = "SAFE";
      monAlert = "NOMINAL PATROL";
      monHeartRate = 74;
      monSpO2 = 98;
      Serial.println(F("[BASE STATION INFO] All squad units reporting SAFE."));
      updateOled();
    } else if (input.startsWith("{")) {
      digitalWrite(PIN_LED_NET, HIGH);
      parsePacket(input);
      digitalWrite(PIN_LED_NET, LOW);
    }
  }

  // 3. Audio-Visual Siren & Flasher Handling
  handleAudioVisuals();

  // 4. Autonomous Pulse Simulation (Every 4s in standby)
  if (!emergencyActive && (now - demoTimer >= 4000)) {
    demoTimer = now;
    digitalWrite(PIN_LED_NET, HIGH);
    delay(40);
    digitalWrite(PIN_LED_NET, LOW);
  }
}

void parsePacket(const String& jsonStr) {
  StaticJsonDocument<512> doc;
  DeserializationError err = deserializeJson(doc, jsonStr);
  if (err) return;

  monSoldierId = doc["origin_id"] | "SOLDIER-01";
  monName = doc["personnel_name"] | "Sepoy Rajesh Kumar";
  monStatus = doc["status"] | "SAFE";
  monAlert = doc["alert_type"] | "PERIODIC";

  JsonObject vitals = doc["vitals"];
  if (!vitals.isNull()) {
    monHeartRate = vitals["heart_rate_bpm"] | 75;
    monSpO2 = vitals["spo2_percent"] | 98;
  }

  JsonObject gps = doc["gps"];
  if (!gps.isNull()) {
    monLat = gps["latitude"] | 35.4211;
    monLon = gps["longitude"] | 77.1095;
  }

  if (monStatus == "EMERGENCY") {
    emergencyActive = true;
    emergencyMuted = false;
  } else {
    emergencyActive = false;
  }

  updateOled();
}

void handleAudioVisuals() {
  if (emergencyActive && !emergencyMuted) {
    unsigned long now = millis();
    if (now - lastSirenToggle >= 220) {
      lastSirenToggle = now;
      sirenToneHigh = !sirenToneHigh;
      digitalWrite(PIN_LED_EMERGENCY, sirenToneHigh ? HIGH : LOW);
      if (sirenToneHigh) {
        tone(PIN_SIREN, 2400, 180);
      } else {
        tone(PIN_SIREN, 1600, 180);
      }
    }
  } else if (emergencyActive && emergencyMuted) {
    // Steady ON to indicate pending rescue operation
    digitalWrite(PIN_LED_EMERGENCY, HIGH);
    noTone(PIN_SIREN);
  } else {
    digitalWrite(PIN_LED_EMERGENCY, LOW);
    noTone(PIN_SIREN);
  }
}

void updateOled() {
  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setCursor(0, 0);

  if (emergencyActive) {
    if (emergencyMuted) {
      oled.print(F("! EMERGENCY (ACK'D) !"));
    } else {
      oled.print(F("!! CASUALTY ALARM !!"));
    }
  } else {
    oled.print(F("SURAKSHA-NET: BASE OK"));
  }
  oled.drawLine(0, 9, 127, 9, SSD1306_WHITE);

  // Soldier ID & Alert
  oled.setCursor(0, 13);
  oled.print(monSoldierId);
  oled.print(F(": "));
  oled.print(monStatus);

  oled.setCursor(0, 24);
  oled.print(F("EVT: "));
  oled.print(monAlert.substring(0, 16));

  // Vitals
  oled.setCursor(0, 36);
  oled.print(F("HR : ")); oled.print(monHeartRate); oled.print(F(" bpm"));
  oled.setCursor(75, 36);
  oled.print(F("O2: ")); oled.print(monSpO2); oled.print(F("%"));

  // Coordinates
  oled.setCursor(0, 48);
  oled.print(F("LAT: ")); oled.print(monLat, 4);
  oled.setCursor(70, 48);
  oled.print(F("LON:")); oled.print(monLon, 3);

  oled.drawLine(0, 58, 127, 58, SSD1306_WHITE);
  oled.display();
}

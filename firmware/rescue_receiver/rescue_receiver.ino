/*
 * ============================================================================
 * SURAKSHA-NET: Smart Soldier Protection, Survival & Rescue System
 * Module: Tactical Rescue Receiver & Gateway Base Station Firmware
 * Target Hardware: ESP32 DevKit V1 + OLED + Alarm Siren + Serial Bridge
 *
 * FUNCTION:
 * Gateway receiver deployed at the Tactical Operating Base (TOB). Receives
 * telemetry packets from wearable and relay nodes, sounds local audio-visual
 * alarms for immediate casualty alerts, displays coordinates on OLED, and
 * streams validated JSON to the Streamlit command dashboard.
 * ============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

// Uncomment to enable physical SX1278 LoRa hardware
// #define USE_PHYSICAL_LORA_RADIO
#ifdef USE_PHYSICAL_LORA_RADIO
  #include <SPI.h>
  #include <LoRa.h>
  #define LORA_SS    5
  #define LORA_RST  14
  #define LORA_DIO0 26
  #define LORA_BAND 866E6
#endif

// Pin Definitions
#define PIN_OLED_SDA        21
#define PIN_OLED_SCL        22
#define PIN_LED_NETWORK      2  // Blue: RF Activity / Packet Received
#define PIN_LED_EMERGENCY    4  // Red: Critical Casualty Strobe
#define PIN_SIREN_BUZZER    15  // Siren / Buzzer
#define PIN_BTN_ACK         14  // Tactile Button to Mute/Acknowledge Alarm

#define SCREEN_WIDTH       128
#define SCREEN_HEIGHT       64
#define SCREEN_I2C_ADDR   0x3C

Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// State Tracking
bool alarmActive = false;
bool alarmMuted = false;
unsigned long lastPacketTimestamp = 0;
unsigned long lastSirenToggle = 0;
bool sirenToneHigh = false;

// Latest Casualty Telemetry Snapshot
String lastAlertOrigin = "NONE";
String lastAlertName = "ALL UNITS NOMINAL";
String lastAlertType = "STANDBY";
float lastLat = 0.0f;
float lastLon = 0.0f;
int lastHR = 0;
int lastSpO2 = 0;

void parseAndDisplayPacket(const String& jsonStr);
void updateGatewayDisplay();
void handleAudioVisualAlarms();

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(PIN_LED_NETWORK, OUTPUT);
  pinMode(PIN_LED_EMERGENCY, OUTPUT);
  pinMode(PIN_SIREN_BUZZER, OUTPUT);
  pinMode(PIN_BTN_ACK, INPUT_PULLUP);

  digitalWrite(PIN_LED_NETWORK, LOW);
  digitalWrite(PIN_LED_EMERGENCY, LOW);
  digitalWrite(PIN_SIREN_BUZZER, LOW);

  Wire.begin(PIN_OLED_SDA, PIN_OLED_SCL);

  if (oled.begin(SSD1306_SWITCHCAPVCC, SCREEN_I2C_ADDR)) {
    oled.clearDisplay();
    oled.setTextColor(SSD1306_WHITE);
    oled.setTextSize(1);
    oled.setCursor(0, 15);
    oled.println(F("SURAKSHA-NET BASE"));
    oled.setCursor(0, 30);
    oled.println(F("Rescue Gateway v1.0"));
    oled.setCursor(0, 45);
    oled.println(F("Listening for Nodes..."));
    oled.display();
  }

  Serial.println(F("\n=================================================="));
  Serial.println(F(" SURAKSHA-NET RESCUE RECEIVER GATEWAY ONLINE"));
  Serial.println(F(" Mode: Command Base Station & Bridge"));
  Serial.println(F("=================================================="));

#ifdef USE_PHYSICAL_LORA_RADIO
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(LORA_BAND)) {
    Serial.println(F("[ERROR] Physical LoRa initialization failed!"));
  } else {
    LoRa.setSpreadingFactor(10);
    LoRa.setSignalBandwidth(125E3);
    Serial.println(F("[OK] Physical LoRa receiver active on 866 MHz."));
  }
#else
  Serial.println(F("[INFO] Serial Bridge Mode Active (Dashboard Telemetry Ingestion)."));
#endif
}

void loop() {
  // 1. Check Acknowledge / Mute Button
  if (digitalRead(PIN_BTN_ACK) == LOW) {
    if (alarmActive) {
      alarmMuted = true;
      alarmActive = false;
      digitalWrite(PIN_SIREN_BUZZER, LOW);
      digitalWrite(PIN_LED_EMERGENCY, LOW);
      Serial.println(F("[ACK] Casualty alert acknowledged and muted by Command Operator."));
      updateGatewayDisplay();
    }
  }

  // 2. Physical LoRa Ingestion
#ifdef USE_PHYSICAL_LORA_RADIO
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String rfPayload = "";
    while (LoRa.available()) {
      rfPayload += (char)LoRa.read();
    }
    digitalWrite(PIN_LED_NETWORK, HIGH);
    parseAndDisplayPacket(rfPayload);
    Serial.println(rfPayload); // Pass through to Dashboard over USB
    digitalWrite(PIN_LED_NETWORK, LOW);
  }
#endif

  // 3. Serial Ingestion (from Simulation Engine or USB Bridge)
  if (Serial.available()) {
    String serPayload = Serial.readStringUntil('\n');
    serPayload.trim();
    if (serPayload.length() > 0 && serPayload.startsWith("{")) {
      digitalWrite(PIN_LED_NETWORK, HIGH);
      parseAndDisplayPacket(serPayload);
      digitalWrite(PIN_LED_NETWORK, LOW);
    }
  }

  // 4. Drive Audio-Visual Siren if in Emergency
  handleAudioVisualAlarms();
}

void parseAndDisplayPacket(const String& jsonStr) {
  StaticJsonDocument<768> doc;
  DeserializationError err = deserializeJson(doc, jsonStr);

  if (err) {
    return; // Ignore corrupted frames
  }

  String status = doc["status"] | "SAFE";
  String origin = doc["origin_id"] | "UNKNOWN";
  String name = doc["personnel_name"] | "Soldier";
  String alert = doc["alert_type"] | "PERIODIC";

  lastAlertOrigin = origin;
  lastAlertName = name;
  lastAlertType = alert;

  JsonObject vitals = doc["vitals"];
  if (!vitals.isNull()) {
    lastHR = vitals["heart_rate_bpm"] | 0;
    lastSpO2 = vitals["spo2_percent"] | 0;
  }

  JsonObject gps = doc["gps"];
  if (!gps.isNull()) {
    lastLat = gps["latitude"] | 0.0f;
    lastLon = gps["longitude"] | 0.0f;
  }

  if (status == "EMERGENCY") {
    alarmActive = true;
    alarmMuted = false;
  } else if (status == "SAFE" && lastAlertOrigin == origin) {
    alarmActive = false;
  }

  updateGatewayDisplay();
}

void handleAudioVisualAlarms() {
  if (alarmActive && !alarmMuted) {
    unsigned long now = millis();
    if (now - lastSirenToggle >= 250) {
      lastSirenToggle = now;
      sirenToneHigh = !sirenToneHigh;
      digitalWrite(PIN_LED_EMERGENCY, sirenToneHigh ? HIGH : LOW);
      if (sirenToneHigh) {
        tone(PIN_SIREN_BUZZER, 2600, 200);
      } else {
        tone(PIN_SIREN_BUZZER, 1800, 200);
      }
    }
  } else {
    digitalWrite(PIN_LED_EMERGENCY, LOW);
    noTone(PIN_SIREN_BUZZER);
  }
}

void updateGatewayDisplay() {
  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setCursor(0, 0);

  if (alarmActive) {
    oled.print(F("!! EMERGENCY RESCUE !!"));
  } else {
    oled.print(F("COMMAND GATEWAY: OK"));
  }
  oled.drawLine(0, 9, 127, 9, SSD1306_WHITE);

  oled.setCursor(0, 13);
  oled.print(lastAlertOrigin);
  oled.print(F(": "));
  oled.print(lastAlertType);

  oled.setCursor(0, 25);
  oled.print(F("HR : ")); oled.print(lastHR); oled.print(F(" bpm"));
  oled.setCursor(75, 25);
  oled.print(F("O2: ")); oled.print(lastSpO2); oled.print(F("%"));

  oled.setCursor(0, 37);
  oled.print(F("LAT: ")); oled.print(lastLat, 4);
  oled.setCursor(0, 48);
  oled.print(F("LON: ")); oled.print(lastLon, 4);

  oled.drawLine(0, 58, 127, 58, SSD1306_WHITE);
  oled.display();
}

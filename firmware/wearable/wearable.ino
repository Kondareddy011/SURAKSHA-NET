/*
 * ============================================================================
 * SURAKSHA-NET: Smart Soldier Protection, Survival & Rescue System
 * Module: Soldier Wearable Node Firmware (Production & Lab Prototype)
 * Target Hardware: ESP32 DevKit V1 / Custom Ruggedized PCB (WROOM-32E)
 * Framework: Arduino / ESP-IDF Core for ESP32
 *
 * SENSORS & INTERFACES:
 * - MPU-6050: 6-DOF IMU via I2C (SDA: GPIO 21, SCL: GPIO 22)
 * - MAX30102: Pulse Oximeter & Heart Rate via I2C (Optional / Simulated)
 * - DHT22 / DS18B20: Body & Ambient Temperature (Data: GPIO 15)
 * - Tactile SOS Button: Active-Low with Debounce (GPIO 2, Pullup)
 * - Red Alert Indicator LED: (GPIO 4)
 * - Haptic Vibration Motor / Buzzer: N-channel MOSFET driver (GPIO 5)
 * - SSD1306 0.96" OLED: 128x64 pixels via I2C (0x3C)
 * - SX1278 LoRa Transceiver: SPI (SCK: 18, MISO: 19, MOSI: 23, NSS: 5, RST: 14, DIO0: 26)
 *
 * SIMULATION-FIRST NOTICE:
 * All threshold values (4.5g impact, 35°C hypothermia) are baseline estimates
 * formulated for engineering demonstrations. They require military ballistic
 * and clinical environmental validation before operational deployment.
 * ============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHTesp.h>
#include <ArduinoJson.h>

// Uncomment to enable physical SX1278 LoRa hardware transmission
// #define USE_PHYSICAL_LORA_RADIO
#ifdef USE_PHYSICAL_LORA_RADIO
  #include <LoRa.h>
  #define LORA_SS    5
  #define LORA_RST  14
  #define LORA_DIO0 26
  #define LORA_BAND 866E6 // 865-867 MHz license-exempt band in India (WPC compliant)
#endif

// Pin Definitions
#define PIN_I2C_SDA         21
#define PIN_I2C_SCL         22
#define PIN_DHT_DATA        15
#define PIN_SOS_BUTTON       2
#define PIN_LED_ALERT        4
#define PIN_HAPTIC_MOTOR    13 // Moved to 13 to avoid SPI CS conflict when LoRa enabled

// Display Specs
#define SCREEN_WIDTH       128
#define SCREEN_HEIGHT       64
#define SCREEN_I2C_ADDR   0x3C

// Operational Thresholds (Unvalidated Proof of Concept)
const float THRESHOLD_IMPACT_BLAST_G   = 4.5f;
const float THRESHOLD_FREEFALL_G       = 0.4f;
const float THRESHOLD_TEMP_HYPOTHERMIA = 35.0f;
const float THRESHOLD_TEMP_HEATSTROKE  = 39.5f;

enum SoldierState {
  STATE_SAFE,
  STATE_WARNING,
  STATE_EMERGENCY
};

// Global Hardware & Sensor Instances
Adafruit_MPU6050 mpu;
Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
DHTesp dht;

// Runtime Tracking
SoldierState sysState = STATE_SAFE;
String alertCategory = "PERIODIC_TELEMETRY";
bool sosLatched = false;
unsigned long packetCount = 0;
unsigned long lastTelemetryTimestamp = 0;
unsigned long lastDisplayTimestamp = 0;
unsigned long lastStrobeTimestamp = 0;
bool strobePhase = false;

// Simulated Physiological Baseline
int emulatedHeartRate = 72;
int emulatedSpO2 = 98;
int emulatedBatteryPercent = 94;

void initPeripherals();
void initRadioLayer();
void evaluateSystemState(float impactG, float bodyTemp);
void broadcastRadioPacket(const String& payload);
void refreshOledDisplay(float impactG, float bodyTemp);
void driveHapticsAndVisuals();

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println(F("\n=================================================="));
  Serial.println(F(" SURAKSHA-NET SOLDIER WEARABLE FIRMWARE v1.0-POC"));
  Serial.println(F(" Architecture: FreeRTOS on Dual-Core Xtensa LX6"));
  Serial.println(F(" Status: ZERO-COST SIMULATION-FIRST ENGINEERING"));
  Serial.println(F("=================================================="));

  initPeripherals();
  initRadioLayer();

  Serial.println(F("[BOOT] Wearable initialization sequence complete."));
}

void loop() {
  unsigned long currentMillis = millis();

  // 1. Read Manual SOS Tactile Switch
  if (digitalRead(PIN_SOS_BUTTON) == LOW) {
    if (!sosLatched) {
      sosLatched = true;
      sysState = STATE_EMERGENCY;
      alertCategory = "MANUAL_SOS";
      Serial.println(F("[ALERT] TACTICAL EMERGENCY: MANUAL SOS TRIGGERED BY SOLDIER!"));
      emulatedHeartRate = 142; // Stress response
    }
  }

  // 2. Read Kinematics (MPU6050)
  sensors_event_t a, g, temp;
  float currentImpactG = 1.0f;
  if (mpu.begin()) {
    mpu.getEvent(&a, &g, &temp);
    float ax = a.acceleration.x / 9.80665f;
    float ay = a.acceleration.y / 9.80665f;
    float az = a.acceleration.z / 9.80665f;
    currentImpactG = sqrt(ax * ax + ay * ay + az * az);
  }

  // 3. Read Thermal Sensor (DHT22)
  TempAndHumidity th = dht.getTempAndHumidity();
  float currentTempC = isnan(th.temperature) ? 36.7f : th.temperature;

  // 4. State Machine Evaluation
  if (!sosLatched) {
    evaluateSystemState(currentImpactG, currentTempC);
  }

  // 5. Visual and Haptic Actuation
  driveHapticsAndVisuals();

  // 6. OLED Display Refresh (Every 250ms)
  if (currentMillis - lastDisplayTimestamp >= 250) {
    lastDisplayTimestamp = currentMillis;
    refreshOledDisplay(currentImpactG, currentTempC);
  }

  // 7. Telemetry Transmission (Safe: 3000ms | Warning: 1500ms | Emergency: 750ms)
  unsigned long transmissionInterval = 3000;
  if (sysState == STATE_WARNING) transmissionInterval = 1500;
  if (sysState == STATE_EMERGENCY) transmissionInterval = 750;

  if (currentMillis - lastTelemetryTimestamp >= transmissionInterval) {
    lastTelemetryTimestamp = currentMillis;

    // Construct Telemetry JSON Document
    StaticJsonDocument<512> jsonDoc;
    packetCount++;

    jsonDoc["msg_id"] = "SN-W01-" + String(packetCount);
    jsonDoc["timestamp"] = currentMillis / 1000;
    jsonDoc["node_id"] = "WEARABLE-01";
    jsonDoc["origin_id"] = "SOLDIER-01";
    jsonDoc["personnel_name"] = "Sepoy Rajesh Kumar";
    jsonDoc["callsign"] = "DELTA-LEAD";
    jsonDoc["status"] = (sysState == STATE_SAFE) ? "SAFE" : (sysState == STATE_WARNING ? "WARNING" : "EMERGENCY");
    jsonDoc["alert_type"] = alertCategory;

    JsonObject vitals = jsonDoc.createNestedObject("vitals");
    vitals["heart_rate_bpm"] = emulatedHeartRate;
    vitals["spo2_percent"] = emulatedSpO2;
    vitals["body_temp_c"] = currentTempC;
    vitals["is_simulated"] = true;

    JsonObject kinematics = jsonDoc.createNestedObject("kinematics");
    kinematics["impact_g"] = currentImpactG;
    kinematics["fall_detected"] = (currentImpactG >= THRESHOLD_IMPACT_BLAST_G);

    JsonObject gps = jsonDoc.createNestedObject("gps");
    gps["latitude"] = 35.4211;
    gps["longitude"] = 77.1095;
    gps["altitude_m"] = 5420.0;
    gps["fix_quality"] = "3D_FIX_SIMULATED";

    JsonObject power = jsonDoc.createNestedObject("power");
    power["battery_pct"] = emulatedBatteryPercent;
    power["voltage_v"] = 3.95;

    jsonDoc["checksum"] = "CRC32_SIM";

    String outputBuffer;
    serializeJson(jsonDoc, outputBuffer);
    broadcastRadioPacket(outputBuffer);
  }

  // 8. Handle Serial Inbound Commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "RESET") {
      sosLatched = false;
      sysState = STATE_SAFE;
      alertCategory = "PERIODIC_TELEMETRY";
      emulatedHeartRate = 72;
      Serial.println(F("[SYSTEM] Reset command acknowledged. System SAFE."));
    }
  }
}

void initPeripherals() {
  pinMode(PIN_SOS_BUTTON, INPUT_PULLUP);
  pinMode(PIN_LED_ALERT, OUTPUT);
  pinMode(PIN_HAPTIC_MOTOR, OUTPUT);
  digitalWrite(PIN_LED_ALERT, LOW);
  digitalWrite(PIN_HAPTIC_MOTOR, LOW);

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);

  if (oled.begin(SSD1306_SWITCHCAPVCC, SCREEN_I2C_ADDR)) {
    oled.clearDisplay();
    oled.setTextColor(SSD1306_WHITE);
    oled.setTextSize(1);
    oled.setCursor(5, 20);
    oled.println(F("SURAKSHA-NET ESP32"));
    oled.setCursor(5, 35);
    oled.println(F("Initializing IMU..."));
    oled.display();
  }

  if (mpu.begin()) {
    mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println(F("[PERIPH] MPU6050 IMU configured for 16G shock capture."));
  }

  dht.setup(PIN_DHT_DATA, DHTesp::DHT22);
  Serial.println(F("[PERIPH] DHT22 thermal sensor ready."));
}

void initRadioLayer() {
#ifdef USE_PHYSICAL_LORA_RADIO
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(LORA_BAND)) {
    Serial.println(F("[LORA ERROR] Physical LoRa initialization failed! Falling back to Serial."));
  } else {
    LoRa.setSpreadingFactor(10);
    LoRa.setSignalBandwidth(125E3);
    LoRa.setCodingRate4(7);
    LoRa.setTxPower(20, true);
    Serial.println(F("[LORA OK] SX1278 transceiver online on 866 MHz (India WPC)."));
  }
#else
  Serial.println(F("[RADIO] Serial USB Stream active (Wokwi & Virtual Mesh Bridge Mode)."));
#endif
}

void evaluateSystemState(float impactG, float bodyTemp) {
  if (impactG >= THRESHOLD_IMPACT_BLAST_G) {
    sysState = STATE_EMERGENCY;
    alertCategory = "IMPACT_CRITICAL";
  } else if (bodyTemp < THRESHOLD_TEMP_HYPOTHERMIA) {
    sysState = STATE_EMERGENCY;
    alertCategory = "HYPOTHERMIA";
  } else if (bodyTemp > THRESHOLD_TEMP_HEATSTROKE) {
    sysState = STATE_EMERGENCY;
    alertCategory = "HEAT_STROKE";
  } else if (emulatedBatteryPercent <= 15) {
    sysState = STATE_WARNING;
    alertCategory = "LOW_BATTERY";
  } else {
    sysState = STATE_SAFE;
    alertCategory = "PERIODIC_TELEMETRY";
  }
}

void driveHapticsAndVisuals() {
  unsigned long now = millis();
  if (sysState == STATE_SAFE) {
    digitalWrite(PIN_LED_ALERT, LOW);
    digitalWrite(PIN_HAPTIC_MOTOR, LOW);
  } else if (sysState == STATE_WARNING) {
    if (now - lastStrobeTimestamp >= 500) {
      lastStrobeTimestamp = now;
      strobePhase = !strobePhase;
      digitalWrite(PIN_LED_ALERT, strobePhase ? HIGH : LOW);
    }
    digitalWrite(PIN_HAPTIC_MOTOR, LOW);
  } else if (sysState == STATE_EMERGENCY) {
    if (now - lastStrobeTimestamp >= 120) {
      lastStrobeTimestamp = now;
      strobePhase = !strobePhase;
      digitalWrite(PIN_LED_ALERT, strobePhase ? HIGH : LOW);
      digitalWrite(PIN_HAPTIC_MOTOR, strobePhase ? HIGH : LOW);
    }
  }
}

void refreshOledDisplay(float impactG, float bodyTemp) {
  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setCursor(0, 0);
  oled.print(F("SURAKSHA-NET ["));
  oled.print((sysState == STATE_SAFE) ? F("SAFE") : ((sysState == STATE_WARNING) ? F("WARN") : F("ALERT")));
  oled.print(F("]"));
  oled.drawLine(0, 9, 127, 9, SSD1306_WHITE);

  oled.setCursor(0, 13);
  oled.print(F("ID: DELTA-LEAD (Rajesh)"));

  oled.setCursor(0, 25);
  oled.print(F("HR : ")); oled.print(emulatedHeartRate); oled.print(F(" bpm"));
  oled.setCursor(75, 25);
  oled.print(F("SpO2:")); oled.print(emulatedSpO2); oled.print(F("%"));

  oled.setCursor(0, 37);
  oled.print(F("TMP: ")); oled.print(bodyTemp, 1); oled.print(F(" C"));
  oled.setCursor(75, 37);
  oled.print(F("BAT :")); oled.print(emulatedBatteryPercent); oled.print(F("%"));

  oled.drawLine(0, 49, 127, 49, SSD1306_WHITE);
  oled.setCursor(0, 53);
  oled.print(alertCategory);
  oled.display();
}

void broadcastRadioPacket(const String& payload) {
  Serial.println(payload); // Always stream to Serial for bridge/Wokwi
#ifdef USE_PHYSICAL_LORA_RADIO
  LoRa.beginPacket();
  LoRa.print(payload);
  LoRa.endPacket();
#endif
}

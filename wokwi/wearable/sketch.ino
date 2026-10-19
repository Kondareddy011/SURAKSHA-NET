/*
 * ============================================================================
 * SURAKSHA-NET: Smart Soldier Protection, Survival & Rescue System
 * Component: Soldier Wearable Node (Wokwi Simulation Firmware)
 * Target MCU: ESP32-WROOM-32 / ESP32 DevKit V1
 *
 * DISCLAIMER:
 * Simulation-First Proof-of-Concept. Physiological and impact thresholds are
 * engineering estimates and have not been certified for live tactical or
 * ballistic deployment.
 * ============================================================================
 */

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHTesp.h>
#include <ArduinoJson.h>

// Pin Configuration
#define PIN_SDA           21
#define PIN_SCL           22
#define PIN_DHT           15
#define PIN_SOS_BTN        2
#define PIN_ALERT_LED      4
#define PIN_BUZZER         5

// OLED Display Parameters
#define SCREEN_WIDTH     128
#define SCREEN_HEIGHT     64
#define OLED_RESET        -1
#define SCREEN_ADDRESS  0x3C

// Engineering Thresholds (UNVALIDATED ESTIMATES)
#define THRESHOLD_IMPACT_G       4.5f
#define THRESHOLD_FREEFALL_G     0.4f
#define THRESHOLD_TEMP_HYPO     35.0f
#define THRESHOLD_TEMP_HEAT     39.5f

// System States
enum NodeState {
  STATE_SAFE,
  STATE_WARNING,
  STATE_EMERGENCY
};

// Global Hardware Handles
Adafruit_MPU6050 mpu;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
DHTesp dht;

// Runtime State Variables
NodeState currentState = STATE_SAFE;
String currentAlert = "PERIODIC_TELEMETRY";
unsigned long lastTelemetryTime = 0;
unsigned long lastDisplayTime = 0;
unsigned long lastBlinkTime = 0;
unsigned long messageSequence = 1000;
bool ledState = false;
bool manualSosLatched = false;

// Debouncing for SOS Push Button
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

// Simulated Biometrics (MAX30102 Emulation)
int simulatedHeartRate = 74;
int simulatedSpO2 = 98;
int simulatedBatteryPct = 89;

void updateDisplay();
void broadcastTelemetry();
void handleActuators();

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println(F("=================================================="));
  Serial.println(F(" SURAKSHA-NET : SOLDIER WEARABLE NODE BOOTING"));
  Serial.println(F(" Status: SIMULATION-FIRST PROOF OF CONCEPT"));
  Serial.println(F(" Target: ESP32 DevKit V1 | FreeRTOS Framework"));
  Serial.println(F("=================================================="));

  // GPIO Initialization
  pinMode(PIN_SOS_BTN, INPUT_PULLUP);
  pinMode(PIN_ALERT_LED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_ALERT_LED, LOW);
  digitalWrite(PIN_BUZZER, LOW);

  // I2C Bus Initialization
  Wire.begin(PIN_SDA, PIN_SCL);

  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("[ERROR] SSD1306 OLED initialization failed!"));
  } else {
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);
    display.setCursor(10, 15);
    display.println(F("SURAKSHA-NET v1.0"));
    display.setCursor(10, 30);
    display.println(F("Soldier Wearable"));
    display.setCursor(10, 45);
    display.println(F("Initializing..."));
    display.display();
    delay(1000);
  }

  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println(F("[WARN] MPU6050 not detected on I2C bus. Using fallback."));
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println(F("[OK] MPU6050 initialized (16G Range, 21Hz LPF)."));
  }

  // Initialize DHT22
  dht.setup(PIN_DHT, DHTesp::DHT22);
  Serial.println(F("[OK] DHT22 environmental sensor online."));

  Serial.println(F("[READY] Wearable unit online. Ready for mission telemetry."));
}

void loop() {
  unsigned long now = millis();

  // 1. SOS Button Reading & Debouncing
  int reading = digitalRead(PIN_SOS_BTN);
  if (reading != lastButtonState) {
    lastDebounceTime = now;
  }
  if ((now - lastDebounceTime) > debounceDelay) {
    if (reading == LOW && !manualSosLatched) {
      manualSosLatched = true;
      currentState = STATE_EMERGENCY;
      currentAlert = "MANUAL_SOS";
      Serial.println(F("[TACTICAL EVENT] MANUAL SOS BUTTON DEPRESSED!"));
      broadcastTelemetry();
    }
  }
  lastButtonState = reading;

  // 2. Read Sensors (MPU6050 & DHT22)
  sensors_event_t a, g, temp;
  float totalAccelG = 1.0f;
  if (mpu.begin()) {
    mpu.getEvent(&a, &g, &temp);
    float ax = a.acceleration.x / 9.80665f;
    float ay = a.acceleration.y / 9.80665f;
    float az = a.acceleration.z / 9.80665f;
    totalAccelG = sqrt(ax * ax + ay * ay + az * az);
  }

  TempAndHumidity dhtData = dht.getTempAndHumidity();
  float bodyTemp = dhtData.temperature;
  if (isnan(bodyTemp) || bodyTemp == 0.0f) {
    bodyTemp = 36.8f; // Fallback to nominal core temperature
  }

  // 3. State Machine Evaluation (Unless already latched into manual SOS)
  if (!manualSosLatched) {
    if (totalAccelG >= THRESHOLD_IMPACT_G) {
      currentState = STATE_EMERGENCY;
      currentAlert = "IMPACT_CRITICAL";
      simulatedHeartRate = 145;
    } else if (bodyTemp < THRESHOLD_TEMP_HYPO) {
      currentState = STATE_EMERGENCY;
      currentAlert = "HYPOTHERMIA";
    } else if (bodyTemp > THRESHOLD_TEMP_HEAT) {
      currentState = STATE_EMERGENCY;
      currentAlert = "HEAT_STROKE";
    } else if (simulatedBatteryPct <= 15) {
      currentState = STATE_WARNING;
      currentAlert = "LOW_BATTERY";
    } else {
      currentState = STATE_SAFE;
      currentAlert = "PERIODIC_TELEMETRY";
    }
  }

  // 4. Actuator Driver (LED & Buzzer)
  handleActuators();

  // 5. Periodic Display Refresh (Every 250ms)
  if (now - lastDisplayTime >= 250) {
    lastDisplayTime = now;
    updateDisplay();
  }

  // 6. Broadcast Telemetry Packet (Every 2000ms in Safe, 1000ms in Warning/Emergency)
  unsigned long telemetryInterval = (currentState == STATE_SAFE) ? 2500 : 1000;
  if (now - lastTelemetryTime >= telemetryInterval) {
    lastTelemetryTime = now;
    broadcastTelemetry();
  }

  // 7. Check for incoming Serial commands (e.g. from Dashboard or Receiver)
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "RESET") {
      manualSosLatched = false;
      currentState = STATE_SAFE;
      currentAlert = "SYSTEM_RESET";
      simulatedHeartRate = 72;
      Serial.println(F("[COMMAND] System reset to SAFE state."));
      broadcastTelemetry();
    } else if (cmd == "SOS") {
      manualSosLatched = true;
      currentState = STATE_EMERGENCY;
      currentAlert = "MANUAL_SOS";
      broadcastTelemetry();
    }
  }
}

void handleActuators() {
  unsigned long now = millis();
  if (currentState == STATE_SAFE) {
    digitalWrite(PIN_ALERT_LED, LOW);
    noTone(PIN_BUZZER);
  } else if (currentState == STATE_WARNING) {
    // 500ms blink rate
    if (now - lastBlinkTime >= 500) {
      lastBlinkTime = now;
      ledState = !ledState;
      digitalWrite(PIN_ALERT_LED, ledState ? HIGH : LOW);
      if (ledState) {
        tone(PIN_BUZZER, 800, 100);
      }
    }
  } else if (currentState == STATE_EMERGENCY) {
    // 150ms rapid strobe
    if (now - lastBlinkTime >= 150) {
      lastBlinkTime = now;
      ledState = !ledState;
      digitalWrite(PIN_ALERT_LED, ledState ? HIGH : LOW);
      if (ledState) {
        tone(PIN_BUZZER, 2400, 80);
      }
    }
  }
}

void updateDisplay() {
  display.clearDisplay();
  
  // Tactical Header
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print(F("SURAKSHA-NET ["));
  if (currentState == STATE_SAFE) {
    display.print(F("SAFE"));
  } else if (currentState == STATE_WARNING) {
    display.print(F("WARN"));
  } else {
    display.print(F("EMERG"));
  }
  display.print(F("]"));

  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);

  // Soldier Callsign
  display.setCursor(0, 14);
  display.print(F("ID: DELTA-01 (Rajesh)"));

  // Biometrics
  display.setCursor(0, 26);
  display.print(F("HR: ")); display.print(simulatedHeartRate); display.print(F(" BPM"));
  display.setCursor(75, 26);
  display.print(F("O2: ")); display.print(simulatedSpO2); display.print(F("%"));

  // Environment & Shock
  TempAndHumidity dhtData = dht.getTempAndHumidity();
  float temp = isnan(dhtData.temperature) ? 36.8f : dhtData.temperature;
  display.setCursor(0, 38);
  display.print(F("TMP: ")); display.print(temp, 1); display.print(F(" C"));
  display.setCursor(75, 38);
  display.print(F("BAT: ")); display.print(simulatedBatteryPct); display.print(F("%"));

  // Alert Footer
  display.drawLine(0, 50, 127, 50, SSD1306_WHITE);
  display.setCursor(0, 54);
  if (currentState == STATE_EMERGENCY) {
    display.print(F("! ")); display.print(currentAlert); display.print(F(" !"));
  } else {
    display.print(F("Link: LORA RELAY OK"));
  }

  display.display();
}

void broadcastTelemetry() {
  StaticJsonDocument<512> doc;
  messageSequence++;

  doc["msg_id"] = "WEARABLE-" + String(messageSequence);
  doc["timestamp"] = millis() / 1000;
  doc["node_id"] = "WEARABLE-01";
  doc["origin_id"] = "SOLDIER-01";
  doc["personnel_name"] = "Sepoy Rajesh Kumar";
  doc["callsign"] = "DELTA-LEAD";

  if (currentState == STATE_SAFE) {
    doc["status"] = "SAFE";
  } else if (currentState == STATE_WARNING) {
    doc["status"] = "WARNING";
  } else {
    doc["status"] = "EMERGENCY";
  }
  doc["alert_type"] = currentAlert;

  JsonObject vitals = doc.createNestedObject("vitals");
  vitals["heart_rate_bpm"] = simulatedHeartRate;
  vitals["spo2_percent"] = simulatedSpO2;
  TempAndHumidity dhtData = dht.getTempAndHumidity();
  vitals["body_temp_c"] = isnan(dhtData.temperature) ? 36.8 : dhtData.temperature;
  vitals["is_simulated"] = true;

  JsonObject kinematics = doc.createNestedObject("kinematics");
  sensors_event_t a, g, temp;
  if (mpu.begin()) {
    mpu.getEvent(&a, &g, &temp);
    kinematics["accel_x_g"] = a.acceleration.x / 9.81;
    kinematics["accel_y_g"] = a.acceleration.y / 9.81;
    kinematics["accel_z_g"] = a.acceleration.z / 9.81;
    float mag = sqrt(pow(a.acceleration.x, 2) + pow(a.acceleration.y, 2) + pow(a.acceleration.z, 2)) / 9.81;
    kinematics["impact_g"] = mag;
    kinematics["fall_detected"] = (mag > THRESHOLD_IMPACT_G);
  } else {
    kinematics["impact_g"] = 1.0;
    kinematics["fall_detected"] = false;
  }

  JsonObject gps = doc.createNestedObject("gps");
  gps["latitude"] = 35.4211;
  gps["longitude"] = 77.1095;
  gps["altitude_m"] = 5420.0;
  gps["fix_quality"] = "3D_FIX_SIMULATED";

  JsonObject network = doc.createNestedObject("network");
  network["rssi_dbm"] = -75;
  network["hop_count"] = 0;
  JsonArray route = network.createNestedArray("route");
  route.add("WEARABLE-01");

  JsonObject power = doc.createNestedObject("power");
  power["battery_pct"] = simulatedBatteryPct;
  power["voltage_v"] = 3.95;
  power["is_low_battery"] = (simulatedBatteryPct <= 15);

  doc["checksum"] = "SIM_CRC32";

  // Serialize to JSON and output over Serial
  serializeJson(doc, Serial);
  Serial.println();
}

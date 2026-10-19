/*
 * ============================================================================
 * SURAKSHA-NET: Smart Soldier Protection, Survival & Rescue System
 * Module: Tactical Relay / Mesh Repeater Node Firmware
 * Target Hardware: ESP32-WROOM-32 / Outdoor Solar-Powered Enclosure
 *
 * FUNCTION:
 * Autonomous hill-top repeater that receives soldier telemetry frames, filters
 * duplicates to prevent RF broadcast storms, increments hop count, and forwards
 * packets to the Tactical Command Base Station.
 * ============================================================================
 */

#include <Arduino.h>
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

// LED Indicators
#define PIN_LED_HEARTBEAT   2  // Blue / Green: Power & Normal Operation
#define PIN_LED_FORWARD     4  // Yellow: Packet Forwarded
#define PIN_LED_FAULT       15 // Red: Jamming / Low Battery

// Repeater Identity
const char* RELAY_NODE_ID = "RELAY-NODE-01";
const char* RELAY_LOCATION = "Ridge Post Alpha (Alt 4,800m)";

// Deduplication Cache (Ring Buffer)
const int DEDUP_CACHE_SIZE = 32;
String seenMsgIds[DEDUP_CACHE_SIZE];
int cacheIndex = 0;

// Runtime Statistics
unsigned long totalReceived = 0;
unsigned long totalForwarded = 0;
unsigned long totalDuplicatesDropped = 0;
unsigned long lastHeartbeatTime = 0;

bool isDuplicate(const String& msgId) {
  for (int i = 0; i < DEDUP_CACHE_SIZE; i++) {
    if (seenMsgIds[i] == msgId) {
      return true;
    }
  }
  seenMsgIds[cacheIndex] = msgId;
  cacheIndex = (cacheIndex + 1) % DEDUP_CACHE_SIZE;
  return false;
}

void processPacket(const String& rawJson);
void sendRelayHeartbeat();

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(PIN_LED_HEARTBEAT, OUTPUT);
  pinMode(PIN_LED_FORWARD, OUTPUT);
  pinMode(PIN_LED_FAULT, OUTPUT);

  digitalWrite(PIN_LED_HEARTBEAT, HIGH);
  digitalWrite(PIN_LED_FORWARD, LOW);
  digitalWrite(PIN_LED_FAULT, LOW);

  Serial.println(F("\n=================================================="));
  Serial.println(F(" SURAKSHA-NET TACTICAL RELAY NODE ONLINE"));
  Serial.print(F(" Node ID: ")); Serial.println(RELAY_NODE_ID);
  Serial.print(F(" Location: ")); Serial.println(RELAY_LOCATION);
  Serial.println(F(" Mode: Self-Healing RF Mesh Telemetry Repeater"));
  Serial.println(F("=================================================="));

#ifdef USE_PHYSICAL_LORA_RADIO
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(LORA_BAND)) {
    Serial.println(F("[ERROR] Physical LoRa radio initialization failed!"));
    digitalWrite(PIN_LED_FAULT, HIGH);
  } else {
    LoRa.setTxPower(20, true);
    LoRa.setSpreadingFactor(10);
    LoRa.setSignalBandwidth(125E3);
    Serial.println(F("[OK] Physical LoRa repeater listening on 866 MHz."));
  }
#else
  Serial.println(F("[INFO] Operating in Serial Loopback / Simulated Mesh Mode."));
#endif
}

void loop() {
  unsigned long now = millis();

  // 1. Check for incoming RF packets
#ifdef USE_PHYSICAL_LORA_RADIO
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String incomingPayload = "";
    while (LoRa.available()) {
      incomingPayload += (char)LoRa.read();
    }
    processPacket(incomingPayload);
  }
#endif

  // 2. Check for incoming Serial packets (Bridge or Simulation input)
  if (Serial.available()) {
    String serialPayload = Serial.readStringUntil('\n');
    serialPayload.trim();
    if (serialPayload.length() > 0 && serialPayload.startsWith("{")) {
      processPacket(serialPayload);
    }
  }

  // 3. Heartbeat Blink (Every 1000ms)
  if ((now / 1000) % 2 == 0) {
    digitalWrite(PIN_LED_HEARTBEAT, HIGH);
  } else {
    digitalWrite(PIN_LED_HEARTBEAT, LOW);
  }

  // 4. Autonomous Repeater Status Heartbeat (Every 10s)
  if (now - lastHeartbeatTime >= 10000) {
    lastHeartbeatTime = now;
    sendRelayHeartbeat();
  }
}

void processPacket(const String& rawJson) {
  totalReceived++;
  StaticJsonDocument<768> doc;
  DeserializationError err = deserializeJson(doc, rawJson);

  if (err) {
    Serial.print(F("[WARN] Corrupt JSON packet rejected: "));
    Serial.println(err.c_str());
    digitalWrite(PIN_LED_FAULT, HIGH);
    delay(50);
    digitalWrite(PIN_LED_FAULT, LOW);
    return;
  }

  String msgId = doc["msg_id"] | "UNKNOWN";
  if (isDuplicate(msgId)) {
    totalDuplicatesDropped++;
    Serial.print(F("[DEDUP] Dropped duplicate message: "));
    Serial.println(msgId);
    return;
  }

  // Modify packet for forwarding
  doc["node_id"] = RELAY_NODE_ID;

  JsonObject net = doc["network"];
  if (!net.isNull()) {
    int hops = net["hop_count"] | 0;
    net["hop_count"] = hops + 1;
    JsonArray route = net["route"];
    if (!route.isNull()) {
      route.add(RELAY_NODE_ID);
    }
  }

  // Re-serialize and transmit forward
  String forwardedPayload;
  serializeJson(doc, forwardedPayload);

  digitalWrite(PIN_LED_FORWARD, HIGH);
#ifdef USE_PHYSICAL_LORA_RADIO
  LoRa.beginPacket();
  LoRa.print(forwardedPayload);
  LoRa.endPacket();
#endif
  Serial.println(forwardedPayload); // Also echo over Serial
  digitalWrite(PIN_LED_FORWARD, LOW);

  totalForwarded++;
  Serial.print(F("[FORWARD] Packet "));
  Serial.print(msgId);
  Serial.print(F(" relayed towards command gateway. (Total: "));
  Serial.print(totalForwarded);
  Serial.println(F(")"));
}

void sendRelayHeartbeat() {
  StaticJsonDocument<256> doc;
  doc["msg_id"] = "HB-" + String(RELAY_NODE_ID) + "-" + String(millis() / 1000);
  doc["node_id"] = RELAY_NODE_ID;
  doc["type"] = "RELAY_STATUS_HEARTBEAT";
  doc["uptime_sec"] = millis() / 1000;
  doc["total_received"] = totalReceived;
  doc["total_forwarded"] = totalForwarded;
  doc["duplicates_dropped"] = totalDuplicatesDropped;
  doc["battery_percent"] = 96; // Simulated solar/buffer battery

  String hbPayload;
  serializeJson(doc, hbPayload);
  Serial.println(hbPayload);
}

# SURAKSHA-NET: Communication Protocol Specification

## 1. Protocol Architecture & Overview
The SURAKSHA-NET communication protocol is designed to provide robust, self-describing, and fault-tolerant telemetry transmission across constrained RF links. In this simulation-first proof of concept, messages are formatted as standardized JSON payloads to facilitate seamless testing, debugging, and visualization.

---

## 2. Telemetry Packet Schema

```json
{
  "msg_id": "SN-W01-1042",
  "timestamp": 1729074000,
  "node_id": "RELAY-NODE-01",
  "origin_id": "SOLDIER-01",
  "personnel_name": "Sepoy Rajesh Kumar",
  "callsign": "DELTA-LEAD",
  "status": "EMERGENCY",
  "alert_type": "IMPACT_CRITICAL",
  "vitals": {
    "heart_rate_bpm": 142,
    "spo2_percent": 91,
    "body_temp_c": 36.4,
    "is_simulated": true
  },
  "kinematics": {
    "accel_x_g": 0.45,
    "accel_y_g": 1.12,
    "accel_z_g": 0.15,
    "impact_g": 5.42,
    "fall_detected": true,
    "is_immobile": true
  },
  "gps": {
    "latitude": 35.4211,
    "longitude": 77.1095,
    "altitude_m": 5420.0,
    "fix_quality": "3D_FIX_SIMULATED"
  },
  "network": {
    "rssi_dbm": -82,
    "snr_db": 7.4,
    "hop_count": 1,
    "route": ["SOLDIER-01", "RELAY-NODE-01", "BASE-COMMAND-01"],
    "backup_route_active": false
  },
  "power": {
    "battery_pct": 74,
    "voltage_v": 3.81,
    "is_low_battery": false
  },
  "checksum": "E289F4C1"
}
```

---

## 3. Field Specification & Validation Rules

| Key | Type | Unit / Range | Validation Rule / Meaning |
| :--- | :--- | :--- | :--- |
| `msg_id` | String | Unique string | Format: `SN-{Node}-{Seq}`. Used for deduplication. |
| `timestamp` | Integer | Epoch seconds | UTC Unix timestamp of message creation. |
| `node_id` | String | Identifier | ID of the transmitting node (updated by relays). |
| `origin_id` | String | Identifier | Immutable ID of the originating wearable unit. |
| `personnel_name` | String | Human readable | Soldier name registered to the wearable unit. |
| `callsign` | String | Tactical string | Squad callsign (e.g. `DELTA-LEAD`, `DELTA-SCOUT`). |
| `status` | Enum | `SAFE` \| `WARNING` \| `EMERGENCY` | Master tactical triage classification. |
| `alert_type` | Enum | Alert categories | Reason code for warning or emergency state. |
| `vitals.heart_rate_bpm` | Integer | 30 to 250 bpm | Heart rate. Values outside [30, 250] rejected. |
| `vitals.spo2_percent` | Integer | 50 to 100% | Blood oxygen saturation. |
| `vitals.body_temp_c` | Float | 20.0 to 45.0 °C | Core/skin temperature. |
| `kinematics.impact_g` | Float | 0.0 to 50.0 g | Peak acceleration magnitude. |
| `kinematics.fall_detected` | Boolean | True / False | Freefall-followed-by-shock flag. |
| `gps.latitude` | Float | -90.0 to +90.0° | Geographic latitude. |
| `gps.longitude` | Float | -180.0 to +180.0°| Geographic longitude. |
| `network.hop_count` | Integer | 0 to 8 | Incremented by each relay to track distance. |
| `network.backup_route_active`| Boolean| True / False | Flagged true when routing over failover relay. |
| `checksum` | Hex String| 8 characters | CRC-32 checksum computed over core fields. |

---

## 4. RF Airtime & Binary Compression Roadmap

### 4.1 Proof of Concept JSON Airtime Analysis
In the current software proof of concept, JSON text payloads are approximately **380 to 450 bytes**.
- On a LoRa channel configured with:
  - Bandwidth: $125\text{ kHz}$
  - Spreading Factor: $\text{SF}10$
  - Coding Rate: $4/7$
  - Payload Size: $420\text{ bytes}$
- The calculated Time on Air (ToA) is approximately **$1,180\text{ ms}$**. While completely acceptable for software simulation, this long airtime in physical deployments would consume battery and increase collision probability.

### 4.2 Production Binary Packing (Protobuf / Bit-Packing)
For the Phase 2 physical hardware roadmap, the protocol transitions to binary packed structs:
```c
struct __attribute__((packed)) CompactTelemetryPacket {
    uint32_t msg_id;           // 4 bytes
    uint32_t timestamp;        // 4 bytes
    uint8_t  soldier_id;       // 1 byte
    uint8_t  status_flags;     // 1 byte (Status: 2b, Alert: 4b, Fall: 1b, Immobile: 1b)
    uint8_t  heart_rate;       // 1 byte (0-255 bpm)
    uint8_t  spo2;             // 1 byte (50-100%)
    uint16_t body_temp_centi;  // 2 bytes (Temp in 0.01 deg C)
    uint16_t impact_centi_g;   // 2 bytes (Impact in 0.01 g)
    int32_t  lat_microdeg;     // 4 bytes (Latitude x 1e6)
    int32_t  lon_microdeg;     // 4 bytes (Longitude x 1e6)
    uint16_t altitude_m;       // 2 bytes (Altitude in meters)
    uint8_t  battery_pct;      // 1 byte (0-100%)
    uint8_t  hop_and_route;    // 1 byte (Hop count & relay index)
    uint16_t crc16;            // 2 bytes (CRC-16 CCITT)
}; // Total Binary Payload: 30 BYTES ONLY!
```
- A **30-byte binary packet** reduces LoRa ToA to **$98\text{ ms}$**—an **$11.8\times$ reduction in RF airtime**, maximizing battery endurance and minimizing electronic warfare intercept risk.

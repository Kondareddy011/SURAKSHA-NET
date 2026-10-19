# SURAKSHA-NET: Hardware Bill of Materials (BOM) & Cost Breakdown

> [!NOTE]
> **COST & COMPONENT NOTICE**:
> All pricing figures are indicative market estimates in **Indian Rupees (INR ₹)** based on prototyping and small-batch sourcing through Indian electronic distributors (Robu.in, Tanotis, Mouser India) as of 2024–2026. Costs exclude import duties and GST.

---

## 1. Subsystem 1: Soldier Wearable Tactical Unit (Per Unit BOM)

### Required Components (Core Telemetry & Triage)
| Item # | Component Description | Part / Module Model | Qty | Unit Cost (INR ₹) | Subtotal (INR ₹) | Status / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | Microcontroller Module | ESP32 DevKit V1 (ESP-WROOM-32, Dual Core, 240MHz) | 1 | ₹420 | ₹420 | **Required** (Core processor) |
| 1.2 | 6-Axis Motion / IMU Sensor | MPU-6050 (3-Axis Accel + 3-Axis Gyro, I2C) | 1 | ₹180 | ₹180 | **Required** (Impact/fall detection) |
| 1.3 | Temperature Sensor | DHT22 / AM2302 (Digital 1-wire, -40°C to +80°C) | 1 | ₹210 | ₹210 | **Required** (Thermal monitoring) |
| 1.4 | RF Transceiver Module | Semtech SX1278 LoRa Module (Ra-02, 433/866 MHz, SPI) | 1 | ₹490 | ₹490 | **Required** (Long-range telemetry) |
| 1.5 | Tactical OLED Screen | SSD1306 0.96" Monochrome I2C OLED (128x64) | 1 | ₹220 | ₹220 | **Required** (Visual status) |
| 1.6 | Manual SOS Button | 12mm Sealed Tactile Pushbutton (Active-Low) | 1 | ₹25 | ₹25 | **Required** (Emergency trigger) |
| 1.7 | High-Lumen Alert LED | 5mm High-Intensity Red LED + 220Ω Resistor | 1 | ₹10 | ₹10 | **Required** (Visual strobe) |
| 1.8 | Haptic Alert Actuator | 10mm Coin Vibration Motor (3V) + 2N7002 MOSFET Driver| 1 | ₹85 | ₹85 | **Required** (Tactile alert) |
| 1.9 | Power Storage | 3.7V 1200mAh LiPo Rechargeable Cell (with PCM) | 1 | ₹380 | ₹380 | **Required** (8-12 hr runtime) |
| 1.10 | Battery Management & LDO | TP4056 USB-C Charger + ME6211 3.3V 500mA LDO | 1 | ₹75 | ₹75 | **Required** (Power regulation) |
| 1.11 | Prototyping PCB & Enclosure| Custom 3D Printed PETG Case + Harness Mount | 1 | ₹350 | ₹350 | **Required** (Mechanical housing) |
| 1.12 | Passives & Wiring | Decoupling caps, pullup resistors, JST connectors | Lot | ₹65 | ₹65 | **Required** |
| **--** | **Core Required Subtotal**| | | | **₹2,510** | |

### Optional Enhancements (Field Upgrade Modules)
| Item # | Component Description | Part / Module Model | Qty | Unit Cost (INR ₹) | Status / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.13 | Pulse Oximeter & Heart Rate| MAX30102 PPG Optical Sensor (I2C) | 1 | ₹380 | *Optional* (Simulated in POC) |
| 1.14 | Low-Power GNSS/GPS Module | ATGM336H / NEO-6M GPS Module (UART) | 1 | ₹490 | *Optional* (Simulated in POC) |
| 1.15 | Mil-Grade Ruggedized Casing | CNC Machined Anodized Aluminum Enclosure (IP68) | 1 | ₹1,200 | *Optional* (Phase 3 field trial) |
| **--** | **Wearable Node Total (Fully Loaded)** | | | **₹4,580** | |

---

## 2. Subsystem 2: Autonomous Tactical Relay Node (Per Unit BOM)

| Item # | Component Description | Part / Module Model | Qty | Unit Cost (INR ₹) | Subtotal (INR ₹) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2.1 | Microcontroller Module | ESP32-WROOM-32E (Bare Module on Carrier) | 1 | ₹350 | ₹350 | Ultra-low power sleep support |
| 2.2 | High-Power LoRa Transceiver| Ebyte E22-900T30D (SX1262/SX1278, +30 dBm, 1W) | 1 | ₹1,250 | ₹1,250 | Up to 15km line-of-sight reach |
| 2.3 | Collinear Fiberglass Antenna| 868MHz 5.8 dBi High-Gain Omnidirectional Antenna | 1 | ₹1,100 | ₹1,100 | N-type connector, weatherproof |
| 2.4 | Solar Power Harvest Unit | 12V 20W Polycrystalline Solar Panel | 1 | ₹1,400 | ₹1,400 | Autonomous remote charging |
| 2.5 | Solar Charge Controller | MPPT Solar Battery Management Board (3S LiFePO4) | 1 | ₹650 | ₹650 | High-efficiency conversion |
| 2.6 | Cold-Resistant Battery Pack | 12.8V 6Ah LiFePO4 Battery Pack (-20°C operational) | 1 | ₹2,800 | ₹2,800 | 5-day autonomy without sun |
| 2.7 | Weatherproof Enclosure | IP67 Die-Cast Aluminum Enclosure with Pole Mount | 1 | ₹1,800 | ₹1,800 | High-altitude weather seal |
| **--** | **Tactical Relay Node Total** | | | | **₹9,350** | |

---

## 3. Subsystem 3: Base Station Gateway Receiver (Per Unit BOM)

| Item # | Component Description | Part / Module Model | Qty | Unit Cost (INR ₹) | Subtotal (INR ₹) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 3.1 | Gateway Microcontroller | ESP32 DevKit V1 | 1 | ₹420 | ₹420 | USB Serial Bridge to PC |
| 3.2 | LoRa Receiver Module | Semtech SX1278 Module with SMA Antenna | 1 | ₹550 | ₹550 | Dedicated RF receiver |
| 3.3 | Command OLED Display | SSD1306 0.96" I2C OLED (128x64) | 1 | ₹220 | ₹220 | Local casualty triage display |
| 3.4 | Acoustic Siren Actuator | 90dB High-Pitch Piezoelectric Buzzer | 1 | ₹65 | ₹65 | Audible casualty alarm |
| 3.5 | Visual Strobe Flasher | 10mm High-Intensity Red Diffused LED | 1 | ₹15 | ₹15 | Visual casualty indicator |
| 3.6 | Operator Acknowledge Switch | 16mm Panel-Mount Pushbutton (Momentary) | 1 | ₹45 | ₹45 | Alarm silence / ACK control |
| 3.7 | Desktop Console Housing | Custom Acrylic / 3D-Printed Desktop Console | 1 | ₹450 | ₹450 | Desk-mount gateway chassis |
| **--** | **Base Station Gateway Total** | | | | **₹1,765** | |

---

## 4. Volume Production Cost Projections (Wearable Units)

| Batch Quantity | Prototype (1-10 Units) | Pilot Batch (100 Units) | Production Batch (1,000 Units) | Production Batch (10,000 Units) |
| :--- | :--- | :--- | :--- | :--- |
| **Estimated Unit Cost** | ₹2,510 - ₹4,580 | ₹1,850 | ₹1,280 | **₹890** |
| **Primary Cost Drivers** | Single-unit retail pricing, hand soldering | Custom 2-layer SMT assembly | Automated pick-and-place, reel pricing | Direct IC wafer sourcing, custom injection molding |

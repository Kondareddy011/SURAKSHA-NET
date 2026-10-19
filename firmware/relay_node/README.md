# SURAKSHA-NET: Tactical Relay / Mesh Repeater Node

## Overview
The Tactical Relay Node acts as an autonomous intermediate hop designed for ruggedized deployment on mountain ridgelines, observation towers, or drone payload bays. In deep valleys, mountain folds, or thick jungle canopy where direct line-of-sight RF transmission between the soldier and base camp is obstructed, this node repeats signals and extends the operational rescue envelope.

---

## Technical Specifications
- **Microcontroller**: ESP32-WROOM-32 (240MHz dual-core)
- **RF Transceiver**: Semtech SX1278 (865–867 MHz license-free ISM band in India)
- **Power Supply**: 12V 20W Solar Panel + MPPT Charge Controller + 3.7V 18650 LiFePO4 battery pack
- **Antenna**: 5.8 dBi High-Gain Omnidirectional Fiberglass Collinear Antenna
- **Ingress Protection**: IP67 Weatherproof enclosure rated for -40°C to +55°C

---

## Deduplication & Flooding Mitigation
To prevent broadcast storms and infinite routing loops:
1. Each incoming packet is parsed to extract the `msg_id`.
2. The `msg_id` is compared against an in-memory ring buffer of the 32 most recently processed message IDs.
3. If a match is detected, the packet is silently discarded.
4. If unique, the node increments `hop_count`, appends its identity to `route`, and transmits with high RF output power (+20 dBm).

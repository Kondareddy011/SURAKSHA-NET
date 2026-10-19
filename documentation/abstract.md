# SURAKSHA-NET: Executive Project Abstract

## Abstract
**SURAKSHA-NET** (*Smart Soldier Protection, Survival & Rescue System*) is a decentralized, IoT-enabled battlefield medical telemetry, automated casualty triage, and emergency rescue network engineered for armed forces and emergency response personnel operating in extreme, non-networked operational environments.

The project addresses the critical military requirement for rapid, automated casualty localization within the "Golden Hour" of combat medicine. Traditional soldier radios rely on conscious manual operation and clear line-of-sight propagation, creating severe failure points during concussive blast trauma, avalanche burial, or mountain-shadow RF occlusion.

SURAKSHA-NET solves these challenges through a **four-tier architecture**:
1. **Wearable Telemetry Node**: An ultra-low-power ESP32-based soldier wearable integrating 6-axis inertial motion sensing (MPU6050), ambient and skin temperature monitoring (DHT22/DS18B20), pulse oximetry ($SpO_2$ and heart rate), a tactile manual SOS switch, haptic vibration alerts, and an organic LED (OLED) tactical status screen.
2. **Autonomous Multi-Sensor Triage Engine**: An on-node firmware state machine that categorizes personnel into `SAFE`, `WARNING`, and `EMERGENCY` operational states using multi-sensor fusion (e.g., blast shock detection $>4.5g$, freefall followed by prolonged immobility, hypothermic core temperature drop $<35.0^\circ\text{C}$, or acute hypoxia).
3. **Self-Healing Tactical Relay Mesh**: Solar-powered autonomous repeaters deployed on elevated terrain that provide RF deduplication, hop-count management, and automatic mesh rerouting to bypass damaged or jammed relay paths.
4. **Tactical Rescue Operations Gateway & Dashboard**: An offline-capable Python/Streamlit command center interfacing with a base station receiver, displaying real-time geospatial coordinates, automated triage cards, vital signs graphs, and emergency transmission audit trails.

### Engineering Methodology: Simulation-First Proof of Concept
To maximize development velocity, eliminate upfront capital expenditure, and de-risk the firmware architecture before physical PCB fabrication, SURAKSHA-NET is developed using a **zero-cost, simulation-first engineering methodology**. The entire embedded and telemetry stack is modeled using Wokwi virtual electronics, Arduino/C++ firmware, and an automated Python testing framework.

> [!NOTE]
> **SIMULATION DISCLOSURE**: All biomedical thresholds, impact forces, and GPS positions presented in this proof-of-concept are simulated in software. They demonstrate architectural feasibility and state-machine determinism, but do not constitute clinical or ballistic certification.

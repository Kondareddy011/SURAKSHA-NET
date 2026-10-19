# SURAKSHA-NET: 3-Minute Demonstration Video Script

**Video Title**: SURAKSHA-NET Proof of Concept: Smart Soldier Protection, Survival & Rescue System  
**Total Runtime**: 2 Minutes 50 Seconds  
**Format**: Split-Screen (Screen Recording of Streamlit Dashboard + Wokwi Simulation + Technical Overlay Badges)  

---

### Sequence 1: Operational Problem & System Introduction [00:00 - 00:35]
- **Visuals**:
  - Dramatic title card: *SURAKSHA-NET: Smart Soldier Protection & Automated Rescue System*.
  - B-roll / Graphic: Satellite topography map of rugged Himalayan ridgelines and mountain ravines.
  - On-screen technical badge: `[SIMULATION-FIRST PROOF OF CONCEPT]`.
- **Narration (Voiceover)**:
  > *"In forward military combat and high-altitude border patrols, casualties can happen in seconds. When an infantry soldier is incapacitated by an explosive blast or buried in an avalanche, they cannot reach for a radio. Today, we demonstrate SURAKSHA-NET: a decentralized, zero-cost software proof-of-concept that combines soldier wearable sensing, autonomous edge casualty triage, and self-healing tactical mesh communications."*

---

### Sequence 2: Wearable Circuit & Wokwi Firmware Simulation [00:35 - 01:15]
- **Visuals**:
  - Full-screen view of browser running `wokwi/wearable/`.
  - Close-up callouts showing the ESP32 DevKit, MPU-6050 accelerometer, SSD1306 OLED, DHT22 sensor, red SOS pushbutton, and buzzer.
  - Mouse clicks the Wokwi Play button (▶). OLED powers up, displaying `SURAKSHA-NET [SAFE]`.
  - Serial monitor prints real-time structured JSON telemetry packets.
- **Narration (Voiceover)**:
  > *"Here in the Wokwi simulation environment, we run the identical Arduino C++ firmware engineered for our wearable prototype. The dual-core ESP32 polls the 6-axis IMU for high-g impacts, samples core temperature, and emulates pulse oximetry. Notice the OLED screen rendering real-time squad vitals while the node streams structured JSON telemetry packets with CRC-32 checksums."*
- **On-Screen Action**:
  - Mouse clicks the red SOS tactile button on the circuit.
  - The red alert LED strobes violently, the buzzer sounds an emergency tone, and the OLED flips to `EMERG`.
- **Narration (Voiceover)**:
  > *"When the soldier presses the tactile SOS switch—or when the IMU detects an impact exceeding 4.5g—the wearable latches into an EMERGENCY state, triggering local audio-visual strobe alerts and shifting the radio into high-rate distress beaconing."*

---

### Sequence 3: Tactical Rescue Command Dashboard [01:15 - 02:00]
- **Visuals**:
  - Switch to browser displaying the Streamlit Tactical Dashboard (`dashboard/app.py`).
  - Dark-slate tactical command interface showing 3 soldiers: Sepoy Rajesh Kumar (Lead), Lance Naik Amit Singh (Scout), and Havildar Vikram Thapa (Support).
  - Highlight the top metric bar (Total Deployed, Safe, Warning, Emergency, Relay Nodes).
  - Highlight the interactive high-altitude GIS map with real-time coordinate pins.
- **Narration (Voiceover)**:
  > *"At the Tactical Operating Base, rescue commanders monitor our offline-capable Streamlit dashboard. Running entirely locally without requiring internet connectivity, the dashboard visualizes vital signs, shock forces, battery levels, and precise geospatial coordinates for every deployed soldier in the sector."*

---

### Sequence 4: Blast Shock Ingestion & Dynamic Mesh Failover [02:00 - 02:35]
- **Visuals**:
  - Mouse hovers over Soldier 1 tab.
  - Clicks `💥 Blast Shock (>5g)`.
  - Instantly, Soldier 1's status card pulses red, displaying `EMERGENCY - IMPACT_CRITICAL (5.60g)`.
  - The tactical summary metric updates to `1 CRITICAL CASUALTY`.
  - The incident is appended to the Mission Event Log at the bottom.
  - Mouse navigates to the sidebar and clicks `Toggle Relay-01` to simulate repeater failure.
  - The active RF route instantly changes from `SOLDIER-01 -> RELAY-01 -> BASE` to `SOLDIER-01 -> RELAY-02 -> BASE (⚡ FAILOVER PATH)`.
- **Narration (Voiceover)**:
  > *"Watch as we inject an explosive shock event: the automated triage engine classifies the trauma immediately. And when we simulate a tactical repeater failure—such as enemy jamming or battery depletion on Ridge-Alpha—SURAKSHA-NET's decentralized routing algorithm automatically hops through our secondary repeater, maintaining critical telemetry without losing a single packet."*

---

### Sequence 5: Automated Testing & Hardware Transition [02:35 - 02:50]
- **Visuals**:
  - Quick split-screen cut to PowerShell terminal running `.\.venv\Scripts\python.exe simulation\test_scenarios.py`.
  - All 22 automated tests pass with `OK` in 0.009 seconds.
  - Final splash screen showing the 4-Phase Hardware Roadmap and project contact details.
- **Narration (Voiceover)**:
  > *"With 100% of our automated regression tests passing and our software architecture fully de-risked at zero cost, SURAKSHA-NET is primed for physical PCB fabrication and field trials. Thank you for joining us in building the next generation of soldier survival technology."*

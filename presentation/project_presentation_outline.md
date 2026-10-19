# SURAKSHA-NET: 16-Slide Master Presentation Deck Outline

**Project Title**: SURAKSHA-NET: Smart Soldier Protection, Survival & Rescue System  
**Presentation Audience**: Defense Evaluation Panels, Technology Incubators, Grant Committees, Corporate CSR Sponsors  

---

### Slide 1: Title & Vision
- **Header**: SURAKSHA-NET
- **Sub-header**: Smart Soldier Protection, Survival & Automated Rescue System
- **Visual**: Tactical emblem featuring a digital shield, soldier silhouette, and mesh RF network overlay.
- **Key Points**:
  - Decentralized Battlefield Medical Telemetry.
  - Autonomous Multi-Sensor Casualty Triage.
  - Zero-Cost Simulation-First Engineering Proof-of-Concept.
- **Speaker Notes**: Introduce the project, team credentials, and state that this represents a completed software proof-of-concept ready for physical transition.

---

### Slide 2: The Tactical Problem: Combat "Golden Hour"
- **Header**: The Fatal Delay in Forward Casualty Care
- **Visual**: Timeline diagram showing mortality curve within the first 60 minutes versus typical search and rescue times (3–12 hours).
- **Key Points**:
  - 90% of potentially survivable combat deaths occur during the Golden Hour.
  - Blast concussions, tension pneumothorax, and severe hemorrhage incapacitate soldiers rapidly.
  - Incapacitated or unconscious soldiers cannot operate traditional Push-to-Talk (PTT) radios.
- **Speaker Notes**: Emphasize that traditional combat net radios depend entirely on a conscious, capable human operator.

---

### Slide 3: Operational Environment Realities
- **Header**: The Contested, Non-Networked Forward Edge
- **Visual**: 3D cross-section of high-altitude mountain ridgelines, glacial folds, and deep river gorges.
- **Key Points**:
  - Non-existent commercial cellular/internet infrastructure in forward posts (LAC, Siachen, counter-insurgency jungles).
  - Mountain shadow occlusion blocking direct RF line-of-sight back to battalion headquarters.
  - Extreme environmental stressors: $-40^\circ\text{C}$ frostbite, hypoxia ($SpO_2 < 85\%$), exertional heatstroke.
- **Speaker Notes**: Highlight that solutions designed for urban policing or cellular smartwatches fail completely in these theaters.

---

### Slide 4: The Proposed Solution: SURAKSHA-NET
- **Header**: Automated, Edge-Resident Soldier Telemetry
- **Visual**: High-level block diagram connecting Soldier Wearable $\rightarrow$ Tactical Relay $\rightarrow$ Base Gateway $\rightarrow$ Rescue Dashboard.
- **Key Points**:
  - Autonomous Edge Computing: Microcontroller evaluates health status on the soldier.
  - Multi-Sensor Fusion: Cross-correlating acceleration, temperature, and vitals to filter out false alarms.
  - Sub-GHz Long-Range Mesh: License-free 865–867 MHz LoRa transmission.
  - Real-Time Command Visibility: Zero-cloud, air-gapped tactical dashboard.
- **Speaker Notes**: Stress the core philosophy: edge intelligence without reliance on external cloud servers.

---

### Slide 5: Multi-Tier System Architecture
- **Header**: 4-Tier Hardware & Software Architecture
- **Visual**: Clean architecture diagram based on `diagrams/system_architecture.mmd`.
- **Key Points**:
  - **Tier 1 (Tactical Edge)**: Wearable sensing node (ESP32, MPU6050, DHT22, OLED, SOS switch).
  - **Tier 2 (Mesh Backhaul)**: Autonomous ridgeline repeaters with deduplication and failover.
  - **Tier 3 (Base Gateway)**: ESP32 hardware receiver with audio siren and casualty strobe.
  - **Tier 4 (Command GUI)**: Offline Python/Streamlit tactical map and incident database.
- **Speaker Notes**: Explain how each tier operates independently, ensuring system survivability even if upper tiers are temporarily disconnected.

---

### Slide 6: Wearable Circuit & Hardware Design
- **Header**: Soldier Wearable Node Schematics
- **Visual**: Circuit schematic based on `diagrams/circuit_architecture.mmd`.
- **Key Points**:
  - ESP32-WROOM-32 dual-core Xtensa microcontroller.
  - MPU-6050 configured for $\pm 16g$ dynamic range (shock capture).
  - SSD1306 OLED for local tactical feedback and silent status checks.
  - Tactile manual SOS switch and coin vibration motor for silent haptic alerts.
- **Speaker Notes**: Walk through the component pinouts, noting that components were selected for cost-efficiency, reliability, and local availability in India.

---

### Slide 7: Autonomous Multi-Sensor Triage Engine
- **Header**: Edge State Machine: Filtering True Trauma from Combat Drills
- **Visual**: State diagram showing transitions between `SAFE`, `WARNING`, and `EMERGENCY`.
- **Key Points**:
  - Blast Shock Detection: Vector magnitude $\ge 4.5g$.
  - Two-Stage Fall Detection: Freefall ($<0.4g$) followed by impact and immobility.
  - Environmental Trauma: Hypothermia ($<35.0^\circ\text{C}$) and heatstroke ($>39.5^\circ\text{C}$).
  - 10-Second Haptic Pre-Alarm Window: Allows a conscious soldier to cancel false alarms.
- **Speaker Notes**: Explain the critical false-alarm mitigation strategy that builds operator trust in the field.

---

### Slide 8: Self-Healing Mesh & Dynamic Failover
- **Header**: Resilient Routing in Non-Line-of-Sight Terrain
- **Visual**: Sequence diagram based on `diagrams/communication_flow.mmd`.
- **Key Points**:
  - Primary path: Wearable $\rightarrow$ Relay-01 $\rightarrow$ Base Station.
  - In-memory 32-message ring buffer prevents duplicate frame broadcast storms.
  - Autonomous dynamic failover: If Relay-01 is destroyed or jammed, packets instantly route via Relay-02.
  - Transparent hop counting and path auditing recorded in every packet.
- **Speaker Notes**: Explain how mountain ridges are conquered using low-cost autonomous repeaters.

---

### Slide 9: Communication Protocol & RF Optimization
- **Header**: Lightweight, Low-Probability-of-Intercept Protocol
- **Visual**: Data structure comparison graphic: JSON text (420 bytes) vs. packed binary struct (30 bytes).
- **Key Points**:
  - Standardized JSON protocol used in simulation proof-of-concept for transparency and verification.
  - CRC-32 checksum integrity sealing.
  - Production binary compression roadmap: $11.8\times$ reduction in Time on Air (ToA down to 98ms).
  - Compliance with Indian WPC 865–867 MHz license-exempt regulations.
- **Speaker Notes**: Discuss RF discipline, power savings, and electronic warfare defense.

---

### Slide 10: Wokwi Electronics Simulation Verification
- **Header**: Zero-Cost Hardware Emulation in Wokwi
- **Visual**: Screenshots of `wokwi/wearable/` and `wokwi/rescue_receiver/` circuits actively running in browser.
- **Key Points**:
  - Exact pin-level emulation of ESP32, MPU-6050, SSD1306, DHT22, and peripherals.
  - Real-time C++ sketch compilation and execution without physical breadboards.
  - Complete project reproducibility via standardized `diagram.json` and `sketch.ino`.
- **Speaker Notes**: Highlight that prospective sponsors can test and interact with the circuit themselves with one click.

---

### Slide 11: Tactical Rescue Command Dashboard
- **Header**: Intuitive, Offline-Capable Mission Control
- **Visual**: Screenshot of Streamlit Dashboard (`dashboard/app.py`) showing tactical cards and GIS map.
- **Key Points**:
  - Real-time squad health metrics with dynamic color-coded urgency states.
  - Interactive geospatial coordinate grid mapping high-altitude patrol positions.
  - Incident injection controls: trigger manual SOS, blast shocks, or relay dropouts live.
  - Complete incident log with one-click CSV/JSON export for post-mission debriefs.
- **Speaker Notes**: Walk through the user interface designed for high-stress command environments.

---

### Slide 12: Automated Testing & Verification Suite
- **Header**: Deterministic Quality Assurance
- **Visual**: Terminal screenshot showing 22 unit tests passing with 100% success rate.
- **Key Points**:
  - Automated test suite (`simulation/test_scenarios.py`) validating:
    - State transition boundaries and priority overrides.
    - Protocol serialization, deserialization, and CRC tamper detection.
    - Out-of-bounds sensor data rejection.
    - Relay failover and duplicate message suppression.
    - Pre-configured mission scenario JSON files.
- **Speaker Notes**: Emphasize engineering rigor—every single core logic rule has automated unit tests.

---

### Slide 13: Hardware Bill of Materials & Unit Economics
- **Header**: Production Feasibility & Indian Supply Chain
- **Visual**: Cost breakdown bar chart showing prototype cost vs. 1,000-unit production cost.
- **Key Points**:
  - Wearable Prototype Cost: ₹2,510 (Core) to ₹4,580 (Fully loaded).
  - Autonomous Solar Relay Node Cost: ₹9,350.
  - Base Station Receiver Cost: ₹1,765.
  - Scale Economics: Projected wearable cost of **₹890 to ₹1,280** in 1,000+ unit batches.
  - Western equivalents cost ₹2,00,000+ per soldier.
- **Speaker Notes**: Demonstrate the massive economic advantage of our architecture for large-scale military procurement.

---

### Slide 14: Technical Risks & Engineering Mitigations
- **Header**: Frank Engineering Appraisal & Safety Mitigations
- **Visual**: Matrix table mapping risks to specific design mitigations.
- **Key Points**:
  - *Risk*: Cold-temperature battery capacity loss at $-40^\circ\text{C}$ $\rightarrow$ *Mitigation*: Sub-zero LiFePO4 cells + body-heat thermal harness placement.
  - *Risk*: PPG optical motion artifacts during sprinting $\rightarrow$ *Mitigation*: IMU-gated vitals sampling + chest dry-electrode roadmap.
  - *Risk*: False alarms during combat maneuvers $\rightarrow$ *Mitigation*: 10-second haptic pre-alarm grace window.
  - *Risk*: Antenna detuning by human body $\rightarrow$ *Mitigation*: Quarter-wave whip with ground plane directed outward.
- **Speaker Notes**: Show investors that the team understands real-world military engineering hurdles and has tangible solutions.

---

### Slide 15: 4-Stage Development Roadmap
- **Header**: From Simulation POC to Fielded Battalion Deployment
- **Visual**: Gantt chart timeline covering Phase 1 through Phase 4.
- **Key Points**:
  - **Phase 1 (Done)**: Software Simulation POC (₹0 budget).
  - **Phase 2 (M1–M3)**: Breadboard & Benchtop Integration + RF Range Testing (₹50k budget).
  - **Phase 3 (M4–M7)**: Custom 4-Layer SMT PCB + IP68 Ruggedized Housing + Beta Squad Trials (₹2.5L budget).
  - **Phase 4 (M8–M12)**: MIL-STD-810H Qualification + WPC ETA Certification + Military Pilot Trials (₹12L–₹15L budget).
- **Speaker Notes**: Present a clear, staged, de-risked pathway with measurable go/no-go gates.

---

### Slide 16: The Sponsorship Ask & Partnership Invitation
- **Header**: Accelerating India's Frontline Soldier Protection
- **Visual**: Summary graphic highlighting the ₹5,00,000 seed funding allocation.
- **Key Points**:
  - **Funding Request**: **₹5,00,000 Seed Grant** for Phase 2 hardware fabrication and rural field trials.
  - **Capital Efficiency**: 100% of funds directed toward physical components, custom PCBs, and instrumentation.
  - **Partner Benefits**: Quarterly milestone reports, priority IP licensing rights, corporate branding, and direct contribution to soldier life-saving technology.
  - **Contact**: SURAKSHA-NET Engineering Team | Open Source Defense Tech Initiative.
- **Speaker Notes**: Close with an inspiring call to action, thanking the panel and opening the floor for technical Q&A.

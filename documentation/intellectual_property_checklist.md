# SURAKSHA-NET: Intellectual Property (IP) & Commercialization Checklist

## 1. Patentability Analysis & Inventions of Interest

### 1.1 Core Inventions Eligible for Patent Protection
1. **Dynamic Multi-Sensor Triage & Correlation Engine**:
   - *Claim Focus*: A method and embedded system for autonomous casualty classification comprising kinematic vector thresholding, post-impact gyroscope angular variance stillness verification, and a timed haptic pre-alarm grace window for false-alarm rejection.
   - *Novelty*: Eliminates false alarms common in single-threshold wearables while ensuring zero-latency distress beacon generation for incapacitated operators without relying on external cloud processing.
2. **Asymmetric Burst-Rate Telemetry State Machine**:
   - *Claim Focus*: A power-conserving and low-probability-of-intercept (LPI) radio frequency communication protocol that dynamically scales packet serialization density, transmit power, and hop repetition intervals based on real-time physiological distress levels.
3. **Autonomous Decentralized Ridgeline Mesh Repeater with Ring-Buffer Deduplication**:
   - *Claim Focus*: An autonomous solar-buffered repeater node executing an in-memory hash ring buffer to prevent broadcast storms and achieve automatic route failover across non-line-of-sight mountain topologies.

### 1.2 Prior Art Search Strategy
- **Databases to Query**: Indian Patent Advanced Search System (InPASS), Google Patents, WIPO Patentscope, USPTO Patent Public Search.
- **Search Keyphrase Combinations**:
  - `("soldier wearable" OR "tactical telemetry") AND ("fall detection" OR "blast shock") AND ("LoRa" OR "mesh network")`
  - `("casualty triage" AND "immobility" AND "haptic" AND "false alarm")`
  - `("mountain repeater" AND "deduplication" AND "failover route")`

---

## 2. Special Defense Provisions: Section 35 of the Indian Patents Act, 1970
Under **Section 35 of the Patents Act, 1970 (Secrecy Directions for Inventions Relevant for Defense Purposes)**:
- Any patent application filed in India that pertains to equipment or technology useful for defense purposes is referred by the Controller of Patents to the **Ministry of Defence (MoD)** or **DRDO** for secrecy review.
- If a secrecy direction is issued, the application cannot be published or granted public visibility until cleared by the MoD.
- *Strategic Guidance*: If filing a domestic patent application, ensure all claims emphasize both defense and civilian first-responder (firefighters, avalanche rescue, underground miners) applications to prevent unintended commercial commercialization delays while maintaining eligibility for defense procurement fast-tracks.

---

## 3. Trademark Protection Strategy
- **Mark**: **SURAKSHA-NET**
- **Target Classes (NICE Classification)**:
  - **Class 9**: Scientific, research, navigation, surveying, photographic, cinematographic, audiovisual, optical, weighing, measuring, signalling, detecting, testing, inspecting, life-saving and teaching apparatus and instruments; wearable activity trackers; communication devices; radios.
  - **Class 42**: Scientific and technological services and research and design relating thereto; industrial analysis and research services; design and development of computer hardware and software.
- **Action Items**: Conduct trademark availability search on the IP India Trade Marks Registry portal prior to external brand marketing.

---

## 4. Open-Source Licensing Boundaries & Freedom to Operate (FTO)

| Module / Component | Applied License | Rationale & Commercial Boundary |
| :--- | :--- | :--- |
| **Streamlit Dashboard (`dashboard/`)** | Apache License 2.0 | Permits open demonstration to sponsors while retaining patent grant rights and trademark protections. |
| **Sensor Simulation Models (`simulation/`)** | MIT License | Maximum compatibility with academic and public testing frameworks. |
| **Arduino Libraries (Adafruit, ArduinoJson)** | MIT / BSD | Permissive open-source licenses allowing proprietary linking and binary distribution without forcing firmware disclosure. |
| **Proprietary Triage Algorithm (Production C++)**| Proprietary / Trade Secret | Kept closed-source in production builds to preserve defense defensibility and venture enterprise value. |

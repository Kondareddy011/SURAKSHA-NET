# SURAKSHA-NET: Smart Soldier Protection, Survival & Rescue System
### Simulation-First IoT & Embedded Systems Proof-of-Concept for Defense Applications
### Upgraded with SURAKSHA AI Assistant (Gemini & Tenglish Support) and Interactive Help Center

[![Python Tests](https://img.shields.io/badge/Tests-28%20Passed-brightgreen)](simulation/test_scenarios.py)
[![AI Integration](https://img.shields.io/badge/AI-Gemini%20%2B%20Local%20Demo-blueviolet)](dashboard/ai_assistant.py)
[![Architecture](https://img.shields.io/badge/Architecture-4--Tier%20Mesh-blue)](diagrams/system_architecture.mmd)
[![Target MCU](https://img.shields.io/badge/Hardware-ESP32%20DevKit%20V1-red)](wokwi/wearable/)
[![Band](https://img.shields.io/badge/RF%20Band-865--867%20MHz%20WPC-orange)](documentation/communication_protocol.md)
[![License](https://img.shields.io/badge/License-Apache%202.0%20%2F%20MIT-lightgrey)](.gitignore)

---

> [!IMPORTANT]
> ### ⚠️ SIMULATION-FIRST ENGINEERING DISCLAIMER
> **SURAKSHA-NET is a zero-cost software proof of concept.**
> - All physiological vital signs ($HR, SpO_2$), body temperatures, and high-g blast impact accelerations are **simulated in software**.
> - All GPS coordinates represent high-altitude sector coordinates emulated for software mapping.
> - Radio transmission timings, packet delivery rates, and failovers represent **software-modeled mesh routing** and do not replace physical RF range qualification.
> - All costs are **indicative market estimates in Indian Rupees (INR ₹)** based on prototyping distributors.
> - No hardware has been certified for military ballistic, live-fire, or clinical medical deployment.
> - The AI Assistant will explain telemetry and simulation events, but will never claim real emergency services have been dispatched.

---

## 1. Upgraded Project Directory Structure

```
SURAKSHA-NET/
│
├── README.md                              # Master engineering documentation & quickstart guide
├── requirements.txt                       # Project root Python dependencies (Streamlit, google-genai, Pytest)
├── .env.example                           # Template for optional GEMINI_API_KEY configuration
├── .gitignore                             # Git ignore rules for virtual environments, secrets, and artifacts
│
├── firmware/                              # Production and lab Arduino/C++ firmware
│   ├── wearable/
│   │   ├── wearable.ino                   # ESP32 Soldier Wearable node firmware (FreeRTOS)
│   │   └── README.md                      # Wearable pinout, state machine & library documentation
│   ├── rescue_receiver/
│   │   ├── rescue_receiver.ino            # Base Station Gateway firmware (Siren, Strobe & Bridge)
│   │   └── README.md                      # Gateway receiver wiring and serial interface docs
│   └── relay_node/
│       ├── relay_node.ino                 # Tactical Autonomous Relay / Repeater firmware
│       └── README.md                      # Mesh deduplication, hop count & power specs
│
├── wokwi/                                 # Zero-cost virtual electronics simulation projects
│   ├── wearable/
│   │   ├── diagram.json                   # Wokwi circuit: ESP32 + MPU6050 + SSD1306 + DHT22 + SOS
│   │   ├── wokwi.toml                     # Wokwi project definition
│   │   ├── sketch.ino                     # Self-contained executable Arduino C++ simulation code
│   │   └── libraries.txt                  # Wokwi dependencies (Adafruit GFX, MPU6050, JSON)
│   └── rescue_receiver/
│       ├── diagram.json                   # Wokwi circuit: ESP32 + SSD1306 + Siren + Strobe + Ack
│       ├── wokwi.toml                     # Wokwi project definition
│       ├── sketch.ino                     # Self-contained receiver simulation code
│       └── libraries.txt                  # Wokwi dependencies
│
├── dashboard/                             # Tactical command and rescue operations GUI
│   ├── app.py                             # Interactive Streamlit command dashboard with 9 sections
│   ├── ai_assistant.py                    # Modular AI service (Gemini API + Local Demo + Tenglish)
│   ├── help_center.py                     # Searchable knowledge base + Interactive Guided Tour
│   ├── ui_components.py                   # Responsive cards, chat bubbles, banners, Web Speech widget
│   ├── simulator.py                       # Multi-node tactical mesh & physiological simulator
│   ├── protocol.py                        # SURAKSHA-NET JSON telemetry protocol & CRC validator
│   └── requirements.txt                   # Dashboard-specific Python requirements
│
├── simulation/                            # Mission scenario datasets and automated test suite
│   ├── scenario_normal.json               # Baseline nominal patrol conditions
│   ├── scenario_warning.json              # Hypothermia and low battery alert scenario
│   ├── scenario_emergency.json            # High-impact blast casualty and SOS trigger scenario
│   ├── scenario_relay_failure.json        # Primary relay failure and dynamic mesh failover
│   └── test_scenarios.py                  # 28 Automated unit tests (100% PASS)
│
├── diagrams/                              # Visual architecture specifications
│   ├── system_architecture.mmd            # 4-tier system hierarchy diagram (Mermaid)
│   ├── circuit_architecture.mmd           # Component schematics and electrical busses (Mermaid)
│   └── communication_flow.mmd             # Emergency sequence and mesh failover flow (Mermaid)
│
├── documentation/                         # Exhaustive technical and commercial engineering docs
│   ├── problem_statement.md               # Battlefield "Golden Hour" and terrain challenges
│   ├── abstract.md                        # Executive summary and architectural novelty
│   ├── proposed_solution.md               # System philosophy and comparative advantage
│   ├── hardware_bom.md                    # Detailed Bill of Materials with unit costs in INR (₹)
│   ├── software_tools.md                  # Stack justification: ESP32, Wokwi, Streamlit, Python
│   ├── system_architecture.md             # Pin mappings, power budget, thermal limits, link budget
│   ├── communication_protocol.md          # Packet schema, validation rules, binary packing roadmap
│   ├── emergency_logic.md                 # Triage state machine, thresholds, false alarm grace window
│   ├── test_plan.md                       # Automated test matrix and manual Wokwi checklist
│   ├── risk_and_limitations.md            # Sub-zero battery risks, PPG artifacts, WPC regulations
│   ├── development_roadmap.md             # 4-phase staged timeline and budget gates
│   ├── sponsor_proposal.md                # ₹5,00,000 seed grant proposal for defense evaluators
│   └── intellectual_property_checklist.md # Patent claims, Section 35 secrecy, trademark strategy
│
└── presentation/                          # Investor and sponsor communication package
    ├── sponsor_pitch.md                   # 5-minute executive pitch script
    ├── demo_video_script.md               # 3-minute video demonstration script with visual cues
    └── project_presentation_outline.md    # 16-slide master presentation deck outline
```

---

## 2. Key Upgrades in Version 2.0

### 🤖 Floating AI Chat Assistant ("Ask SURAKSHA AI")
- **Floating Launcher Button**: Positioned at bottom-right (`Ask SURAKSHA AI 🤖`) with gentle pulsing glow.
- **Multilingual Understanding**: Supports natural-language queries in **English** and **Tenglish** (Telugu-English mixed language), e.g., *"Soldier 1 status cheppu"*, *"SOS ela panchestundi?"*, or *"Explain the dashboard."*
- **Gemini API Integration**: Optional live generative AI powered by `GEMINI_API_KEY`.
- **Intelligent Local Demo Engine**: If no key is set, the system seamlessly falls back to a verified, rule-based semantic assistant labeled as `🤖 Demo Assistant (Rule-Based | No API Key Required)`.
- **Context-Aware Triage**: The AI automatically incorporates real-time telemetry from the simulation (active personnel, current casualty count, relay status, and active route).
- **Suggested Prompt Chips**: Clickable prompt pills for rapid interaction.
- **Voice Support**: Browser-native Web Speech API microphone input and Text-to-Speech (TTS) response readout.

### 📖 Dedicated Help Assistant & Interactive Guided Tour
- **"Guide Me" Walkthrough**: Step-by-step tour walking beginners through all 8 key operational phases with *Previous*, *Next*, and *Exit* controls.
- **Searchable Topic Cards**: Instant keyword filtering across 8 comprehensive topics (overview, telemetry metrics, personnel status, SOS simulations, relay failover, logs, troubleshooting, and Windows execution).

### 🧭 9 Clear Dashboard Sections
1. **Home Dashboard**: Quick tactical summary, persistent emergency banner, and 6 quick-action buttons.
2. **Personnel Monitoring**: In-depth telemetry, vital graphs, and individual soldier simulation triggers.
3. **AI Assistant**: WhatsApp/Gemini-style conversational interface.
4. **Emergency Simulation**: Safe trauma testing with structured event summaries and recommended actions.
5. **Network & Relay Status**: Mesh topology, primary vs. backup relay controls, and RSSI/SNR signal diagnostics.
6. **Map & Sector View**: High-altitude GIS tactical sector map.
7. **Event Logs**: Chronological mission log with severity filtering and CSV export.
8. **Help & User Guide**: Searchable knowledge base and interactive walkthrough.
9. **Project Information**: Hardware BOM in INR (₹), roadmap, and IP specifications.

---

## 3. Quickstart Guide (Windows PowerShell)

### Step 1: Environment Setup & Dependencies
```powershell
# Navigate into the project folder
cd c:\Users\DELL\OneDrive\Desktop\SURAKSHA-NET

# Create Python virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements (Streamlit, google-genai, Pytest, Pandas, Altair)
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### Step 2: (Optional) Configure Gemini API Key
To enable live generative AI responses instead of the built-in local demo engine:
```powershell
# Set environment variable in PowerShell:
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"

# Or copy template to .env:
Copy-Item .env.example .env
```
*(If omitted, the dashboard automatically runs with the high-performance local demo assistant with zero external network requests).*

### Step 3: Run Automated Test Suite
Execute the 28-test automated regression suite:
```powershell
.\.venv\Scripts\python.exe simulation\test_scenarios.py
```
*Or via pytest:*
```powershell
.\.venv\Scripts\pytest.exe -v simulation\test_scenarios.py
```
> **Test Status**: `28 passed in 2.40s` (Validates state transitions, blast impact $>4.5g$, hypothermia, CRC-32 checksums, mesh failover, duplicate suppression, AI fallback, Tenglish query parsing, and Help Center topics).

### Step 4: Launch Tactical Rescue Dashboard
Start the Streamlit application:
```powershell
.\.venv\Scripts\streamlit.exe run dashboard\app.py
```
- Open `http://localhost:8501` in your browser.
- Use the sidebar navigation to move between the 9 sections.
- Click the floating **"Ask SURAKSHA AI"** pill at the bottom-right on any page to open the tactical assistant!

---

## 4. Running Wokwi Virtual Electronics Simulations

The complete embedded hardware circuits are simulated in Wokwi without physical hardware:

1. **Soldier Wearable Simulation ([`wokwi/wearable/`](wokwi/wearable)):**
   - Open [wokwi.com](https://wokwi.com) $\rightarrow$ Select **ESP32 DevKit V1**.
   - Load `diagram.json`, `sketch.ino`, and `libraries.txt` from `wokwi/wearable/`.
   - Click **Play (▶)** to test the OLED screen, MPU-6050 shock sensing, and tactile SOS button.
2. **Tactical Rescue Receiver Simulation ([`wokwi/rescue_receiver/`](wokwi/rescue_receiver)):**
   - Open [wokwi.com](https://wokwi.com) and load files from `wokwi/rescue_receiver/`.
   - Click **Play (▶)**. Type `EMERGENCY` in the Serial Monitor to test the 90dB siren and strobe; click `btn_ack` to mute.

---

## 5. Indicative Hardware Bill of Materials (INR ₹)

| Node Subsystem | Prototype (1-10 Units) | Batch (100 Units) | Scale (1,000+ Units) |
| :--- | :--- | :--- | :--- |
| **Soldier Wearable Unit (Core)** | ₹2,510 | ₹1,850 | **₹890** |
| **Autonomous Solar Relay Node** | ₹9,350 | ₹7,200 | **₹4,600** |
| **Base Station Gateway Console** | ₹1,765 | ₹1,250 | **₹780** |

*See [`documentation/hardware_bom.md`](documentation/hardware_bom.md) for full part-by-part breakdown.*

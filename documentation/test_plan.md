# SURAKSHA-NET: Verification & Test Plan

## 1. Automated Test Suite Execution

The SURAKSHA-NET project includes a comprehensive, deterministic Python automated test suite located at `simulation/test_scenarios.py`.

### 1.1 Prerequisites & Virtual Environment Setup (Windows PowerShell)
```powershell
# Navigate to project root
cd c:\Users\DELL\OneDrive\Desktop\SURAKSHA-NET

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify Python version (Requires Python 3.10+)
python --version
```

### 1.2 Running the Automated Test Suite
Execute the automated test suite using either Python's built-in `unittest` runner or `pytest`:

```powershell
# Option A: Standard Library Unittest Runner
.\.venv\Scripts\python.exe simulation\test_scenarios.py

# Option B: Pytest Runner with Verbose Reporting
.\.venv\Scripts\pytest -v simulation\test_scenarios.py
```

### 1.3 Expected Automated Test Coverage Matrix
| Test Case ID | Target Functionality | Verification Criteria | Expected Result |
| :--- | :--- | :--- | :--- |
| `TC-01` | Nominal State Evaluation | Nominal vitals return `SAFE` & `PERIODIC_TELEMETRY` | **PASS** |
| `TC-02` | Manual SOS Priority | Manual button press overrides all physiological telemetry | **PASS** |
| `TC-03` | Blast Shock Detection | Impact $\ge 4.5g$ triggers `EMERGENCY` & `IMPACT_CRITICAL` | **PASS** |
| `TC-04` | Fall with Immobility | Fall flag + stillness triggers `EMERGENCY` | **PASS** |
| `TC-05` | Hypothermia Detection | Body temperature $< 35.0^\circ\text{C}$ triggers `EMERGENCY` | **PASS** |
| `TC-06` | Heatstroke Detection | Body temperature $> 39.5^\circ\text{C}$ triggers `EMERGENCY` | **PASS** |
| `TC-07` | Low Battery Warning | Battery $\le 20\%$ triggers `WARNING` | **PASS** |
| `TC-08` | Protocol Serialization | JSON serialization round-trip maintains exact values | **PASS** |
| `TC-09` | CRC-32 Checksum Seal | Corrupted bit in telemetry payload invalidates checksum | **PASS** |
| `TC-10` | Invalid HR Rejection | Heart rate $> 250\text{ bpm}$ or $< 30\text{ bpm}$ rejected | **PASS** |
| `TC-11` | Invalid $SpO_2$ Rejection| $SpO_2 > 100\%$ rejected as non-physiological | **PASS** |
| `TC-12` | Out-of-Bounds GPS | Latitude $> 90^\circ$ rejected | **PASS** |
| `TC-13` | Primary Route Discovery | Default route matches `Soldier -> Relay-01 -> Base` | **PASS** |
| `TC-14` | Relay Failover Mesh | Toggling `RELAY-01` offline reroutes via `RELAY-02` | **PASS** |
| `TC-15` | Duplicate Suppression | Duplicate `msg_id` dropped by relay cache | **PASS** |
| `TC-16` | System Reset Recovery | Reset command clears latch and restores `SAFE` state | **PASS** |
| `TC-17` | Scenario JSON Integrity | Validates syntax of all 4 mission scenario JSON files | **PASS** |

---

## 2. Manual Wokwi Circuit Verification Checklist

Because physical hardware has not yet been manufactured, the electronic circuits must be manually simulated in Wokwi.

### 2.1 Wearable Node Project (`wokwi/wearable/`)
1. **Open Wokwi**: In Google Chrome or Edge, navigate to [wokwi.com](https://wokwi.com).
2. **Start ESP32 Project**: Select *ESP32 DevKit V1*.
3. **Load Files**:
   - Replace `diagram.json` with contents of `wokwi/wearable/diagram.json`.
   - Replace `sketch.ino` with contents of `wokwi/wearable/sketch.ino`.
   - Replace `libraries.txt` with contents of `wokwi/wearable/libraries.txt`.
4. **Click Simulation Play Button (▶)**:
   - [ ] Verify OLED initializes with `SURAKSHA-NET [SAFE]`.
   - [ ] Verify Serial Monitor prints JSON telemetry packets every 2.5 seconds.
5. **Interactive Component Testing**:
   - [ ] **Test SOS Button**: Click the red tactile pushbutton (`btn_sos`). Verify:
     - Red Alert LED flashes rapidly (150ms cycle).
     - Haptic buzzer emits emergency alarm tone.
     - OLED transitions from `SAFE` to `EMERG`.
     - Serial Monitor emits `alert_type: "MANUAL_SOS"`.
   - [ ] **Test Reset Command**: In Serial Monitor input box, type `RESET` and press Enter. Verify system returns to `SAFE` state.
   - [ ] **Test DHT22 Temperature**: Click the DHT22 sensor, drag temperature slider below 35°C. Verify system transitions to `HYPOTHERMIA` alert.

---

### 2.2 Base Station Receiver Project (`wokwi/rescue_receiver/`)
1. **Open Wokwi**: Select *ESP32 DevKit V1*.
2. **Load Files**:
   - Replace `diagram.json` with contents of `wokwi/rescue_receiver/diagram.json`.
   - Replace `sketch.ino` with contents of `wokwi/rescue_receiver/sketch.ino`.
   - Replace `libraries.txt` with contents of `wokwi/rescue_receiver/libraries.txt`.
3. **Click Simulation Play Button (▶)**:
   - [ ] Verify OLED renders `SURAKSHA-NET BASE - Tactical Receiver`.
   - [ ] Verify blue Network LED flashes periodically.
4. **Interactive Ingestion Testing**:
   - [ ] In Serial Monitor input box, type `EMERGENCY` and press Enter.
   - [ ] Verify red casualty strobe flashes.
   - [ ] Verify dual-tone 90dB acoustic siren sounds.
   - [ ] Verify OLED displays `!! CASUALTY ALARM !!` with soldier callsign and GPS coordinates.
   - [ ] Click the green tactile button (`btn_ack`) on the circuit.
   - [ ] Verify siren mutes and red LED becomes steady ON (Acknowledged state).

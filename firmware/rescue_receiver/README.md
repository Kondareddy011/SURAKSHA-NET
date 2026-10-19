# SURAKSHA-NET: Tactical Rescue Receiver & Gateway Base Station

## Overview
The Rescue Receiver acts as the base station command gateway deployed at the Tactical Operating Base (TOB), field hospital, or mobile command vehicle. It provides an immediate physical operator interface (audible siren, visual emergency strobe, acknowledge button, and local OLED) while streaming decoded JSON frames over USB Serial to the Streamlit Command Dashboard.

---

## Hardware Pinout & Wiring Table

| Component | Pin / Bus | ESP32 GPIO | Operating Voltage | Function |
| :--- | :--- | :--- | :--- | :--- |
| **SSD1306 OLED** | SDA | GPIO 21 | 3.3V | I2C Data |
| | SCL | GPIO 22 | 3.3V | I2C Clock |
| | VCC / GND | 3V3 / GND | 3.3V | Power Rail |
| **Network LED** | Anode (+) | GPIO 2 | 3.3V via 220Ω | RF Ingestion pulse indicator |
| **Emergency Strobe**| Anode (+) | GPIO 4 | 3.3V via 220Ω | High-intensity emergency flasher |
| **Alarm Siren** | Positive | GPIO 15 | 3.3V / 5V | Dual-tone acoustic emergency alert |
| **Acknowledge Btn** | PIN 1 | GPIO 14 | 3.3V (Pullup) | Operator Mute / Reset tactile switch |
| **LoRa SX1278 (Opt)**| SPI | 18, 19, 23 | 3.3V | LoRa physical RF receiver interface |
| | CS, RST, DIO0 | 5, 14, 26 | 3.3V | Control pins |

---

## Serial Dashboard Integration
The receiver communicates with the Python Streamlit dashboard at **115200 baud**. Any incoming RF packet is verified and emitted over USB Serial as a standard newline-terminated JSON object matching the SURAKSHA-NET Protocol.

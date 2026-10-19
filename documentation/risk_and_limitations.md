# SURAKSHA-NET: Technical Risks, Limitations & Regulatory Challenges

## 1. Battery Chemistry & Sub-Zero Operational Risks

### 1.1 Cold-Temperature Lithium Degradation
Standard Lithium-Polymer (LiPo) and Lithium-Ion (Li-Ion NMC) chemistries experience catastrophic capacity drop when operated at temperatures below $-10^\circ\text{C}$:
- At Siachen / Ladakh operational temperatures ($-20^\circ\text{C}$ to $-40^\circ\text{C}$), standard liquid electrolytes freeze, internal resistance spikes by over $600\%$, and usable discharge capacity drops to less than $20\%$ of nominal rating.
- Attempting to recharge Li-Ion cells below $0^\circ\text{C}$ causes metallic lithium plating on the anode, resulting in internal short-circuits and violent thermal runaway.

### 1.2 Engineering Mitigations Planned
1. **Lithium Iron Phosphate (LiFePO4)**: Sourcing specialized sub-zero LiFePO4 cells rated for continuous discharge down to $-30^\circ\text{C}$.
2. **Body Heat Harvesting / Thermal Placement**: Designing the wearable harness so that the battery pouch sits directly against the soldier’s inner thermal garment, leveraging human metabolic heat ($37^\circ\text{C}$) to keep the battery within safe operating temperatures ($>15^\circ\text{C}$).
3. **Internal PTC Self-Heating Elements**: Utilizing ultra-thin Kapton heating film powered by the solar relay during daytime to warm relay battery packs.

---

## 2. Biomedical Sensor Accuracy & Motion Artifacts

### 2.1 Photoplethysmography (PPG) Limitations in Combat
While optical pulse oximeters (such as the MAX30102) perform adequately on resting hospital patients, they face severe physical limitations on combat soldiers:
- **Severe Motion Artifacts**: Running, firing weapons, or crawling causes relative movement between the optical photodiode and the skin, introducing broad-spectrum motion noise that overwhelms the subtle pulsatile arterial signal.
- **Cold-Induced Peripheral Vasoconstriction**: In high-altitude or sub-zero environments, the human body shunts blood from the extremities to vital core organs. Capillary blood flow in fingers and wrists drops dramatically, causing optical PPG sensors to report zero or falsely low $SpO_2$ ($<70\%$).
- **Sweat & Ballistic Dirt Ingress**: Mud, perspiration, and soot obscure the optical emitter window.

### 2.2 Engineering Mitigations Planned
1. **Multi-Sensor Gating**: Rejecting PPG vital updates during periods of high accelerometer activity ($>1.5g$).
2. **ECG Lead Alternatives**: Transitioning in Phase 3 to chest-strap dry-contact biopotential electrodes (e.g. AD8232) rather than wrist-worn optical sensors.

---

## 3. Radio Frequency & Regulatory Compliance (India WPC / DoT)

### 3.1 Spectrum Regulations in India
The operation of RF transceivers in India is governed by the **Wireless Planning & Coordination (WPC) Wing** of the Department of Telecommunications (DoT):
- **865–867 MHz Band**: De-licensed under GSR 564(E) for low-power wireless equipment.
  - Maximum Transmit Power (EIRP): **$1\text{ Watt}$ ($+30\text{ dBm}$)**.
  - Maximum Channel Bandwidth: **$200\text{ kHz}$**.
  - Must comply with non-interference and non-exclusive usage rules.
- **433.05–434.79 MHz Band**: Restricted to lower power ($10\text{ mW}$ / $+10\text{ dBm}$) with strict duty-cycle limitations, making it unsuitable for multi-kilometer military repeaters.

### 3.2 Human Body Antenna Detuning & SAR Limits
- When a soldier wears an RF antenna directly against the torso, human tissue (consisting primarily of saltwater and dielectric muscle) absorbs RF energy and significantly detunes the antenna.
- Proximity to human flesh can cause **$10\text{ dB}$ to $18\text{ dB}$ of signal attenuation**, severely degrading link budget.
- **Mitigation**: Utilizing a quarter-wave flexible whip antenna mounted atop the shoulder harness with a dedicated metallic ground-plane reflector directed away from the soldier's body.

---

## 4. False-Alarm Hazards & Combat Trust
If a soldier telemetry system sounds false casualty alarms during live combat patrols, commanders will quickly lose trust in the device and switch it off.
- **Mitigation**: Dual-threshold correlation (impact followed by verified stillness) and the mandatory 10-second soldier haptic cancellation window described in `emergency_logic.md`.

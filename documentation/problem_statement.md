# SURAKSHA-NET: Problem Statement & Operational Context

## 1. Executive Context
Modern infantry soldiers and border reconnaissance patrols routinely operate in extreme, hostile, and geographically isolated terrains—from the glacial heights of Siachen and Ladakh (-40°C, 18,000+ ft AMSL) to the hyper-dense jungles of the North-East and the arid heat of the Thar Desert (+50°C). In these forward operational areas, conventional communication infrastructure does not exist, and environmental hazards pose as lethal a threat as enemy combatants.

---

## 2. The Core Tactical Challenges

### 2.1 The "Golden Hour" Combat Casualty Crisis
In combat medicine, the **Golden Hour** dictates that 90% of potentially survivable battlefield fatalities—primarily from catastrophic hemorrhage, blast-induced trauma, and tension pneumothorax—occur within 60 minutes of injury. 
- In forward patrol scenarios, if a soldier is ambushed, thrown by an IED explosion, or buried in an avalanche, **command elements have zero visibility** on the soldier's vital status or precise coordinate.
- Search and rescue operations frequently face delays of 3 to 12 hours simply attempting to localize casualties in broken terrain.

### 2.2 Inability of Injured Personnel to Call for Help
Standard infantry voice radios (VHF/UHF combat net radios) require the soldier to:
1. Remain fully conscious and physically capable.
2. Manually reach for a Push-To-Talk (PTT) switch.
3. Verbally communicate coordinates and injury triage status.

If a soldier suffers a concussive blast shock, hypothermic stupor, or catastrophic blood loss, **manual voice distress calls are impossible**. Without an automated, autonomous physiological monitor that can detect trauma and transmit independently, casualties remain untriaged.

### 2.3 Non-Existent Cellular & Obstructed Line-of-Sight RF
Forward operating environments feature:
- **Zero Commercial Infrastructure**: Commercial cellular networks (4G/5G) and public internet connectivity are non-existent.
- **Deep Mountain Folds & Shadow Zones**: Mountain ridgelines and river gorges obstruct direct line-of-sight (LOS) radio propagation between foot patrols and battalion command posts.
- **RF Signature Vulnerability**: Continuous high-power voice transmissions are easily intercepted and localized by enemy Electronic Support Measures (ESM) and RF direction-finding equipment.

### 2.4 Environmental Biomechanical Hazards
Infantry personnel face non-combat environmental threats that rapidly incapacitate troops:
- **Severe Hypothermia & Frostbite** in sub-zero snowfields.
- **Exertional Heatstroke & Dehydration** in desert theaters.
- **High-Altitude Pulmonary / Cerebral Edema (HAPE/HACE)** characterized by silent oxygen desaturation ($SpO_2 < 85\%$).

---

## 3. Objective of SURAKSHA-NET
To engineer a ruggedized, lightweight, low-cost soldier wearable protection and automated triage system that:
1. Autonomously detects physical trauma (blast shocks $>4.5g$, catastrophic falls, immobility).
2. Continuously monitors vital signs (heart rate, blood oxygenation, core temperature).
3. Transmits distress beacons via a decentralized, low-power RF mesh network without requiring cellular towers or manual intervention.
4. Provides tactical commanders with real-time geospatial triage mapping on an offline-capable rescue dashboard.

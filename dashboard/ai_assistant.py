"""
SURAKSHA-NET Modular AI Assistant Service
Smart Tactical Assistant supporting both Gemini API integration and an intelligent local demo engine.
Supports English and Tenglish (Telugu-English mixed language) queries.
"""

import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Attempt to import Streamlit safely
try:
    import streamlit as st
except ImportError:
    st = None


class SurakshaAIAssistant:
    """
    Tactical AI Assistant for SURAKSHA-NET.
    Integrates with Google Gemini API when GEMINI_API_KEY is configured.
    Falls back gracefully to an intelligent rule-based / semantic local engine when
    no key is set or when network/API limits occur.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", force_local: bool = False):
        self.model_name = model_name
        self.force_local = force_local
        self._api_key = None if force_local else self._resolve_api_key()
        self._client = None
        if not force_local:
            self._init_live_client()

    def _resolve_api_key(self) -> Optional[str]:
        """Securely reads API key from environment variable or Streamlit secrets without logging."""
        # 1. Environment variable
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        if key:
            return key

        # 2. Streamlit secrets (if available)
        if st is not None:
            try:
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    key = str(st.secrets["GEMINI_API_KEY"]).strip()
                    if key:
                        return key
            except Exception:
                pass

        return None

    def _init_live_client(self):
        """Attempts to initialize google-genai client if API key is present."""
        if not self._api_key:
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        except Exception:
            self._client = None

    @property
    def is_live_ai_available(self) -> bool:
        """Returns True if a live Gemini API client is initialized."""
        return self._client is not None

    def build_telemetry_context(self, sim: Any, current_page: str = "Home Dashboard") -> str:
        """Constructs a safe, read-only situational awareness summary for the AI."""
        if sim is None or not hasattr(sim, "soldiers"):
            return "Telemetry status: Simulator offline or uninitialized."

        total = len(sim.soldiers)
        safe_cnt = sum(1 for s in sim.soldiers.values() if s.get("status") == "SAFE" or getattr(s.get("status"), "value", "") == "SAFE")
        warn_cnt = sum(1 for s in sim.soldiers.values() if s.get("status") == "WARNING" or getattr(s.get("status"), "value", "") == "WARNING")
        emerg_cnt = sum(1 for s in sim.soldiers.values() if s.get("status") == "EMERGENCY" or getattr(s.get("status"), "value", "") == "EMERGENCY")

        r1_status = "ONLINE" if sim.relay_status.get("RELAY-01", {}).get("operational") else "OFFLINE"
        r2_status = "ONLINE" if sim.relay_status.get("RELAY-02", {}).get("operational") else "OFFLINE"

        personnel_summary = []
        for s_id, s in sim.soldiers.items():
            status_val = s["status"].value if hasattr(s["status"], "value") else str(s["status"])
            alert_val = s["alert_type"].value if hasattr(s["alert_type"], "value") else str(s["alert_type"])
            hr = s["vitals"].heart_rate_bpm
            spo2 = s["vitals"].spo2_percent
            temp = s["vitals"].body_temp_c
            impact = s["kinematics"].impact_g
            fall = s["kinematics"].fall_detected
            immobile = s["kinematics"].is_immobile
            bat = s["power"].battery_pct

            personnel_summary.append(
                f"- [{s_id}] {s['callsign']} ({s['name']}): Status={status_val}, Alert={alert_val}, HR={hr}bpm, "
                f"SpO2={spo2}%, Temp={temp:.1f}C, Impact={impact:.2f}g, Fall={fall}, Immobile={immobile}, Battery={bat}%"
            )

        recent_events = []
        for ev in sim.event_log[:3]:
            recent_events.append(
                f"[{ev.get('timestamp')}] {ev.get('origin_id')} - {ev.get('alert_type')} ({ev.get('delivery')}) via {ev.get('route')}"
            )

        context = (
            f"CURRENT SIMULATED SYSTEM STATE:\n"
            f"- Current Active Page: {current_page}\n"
            f"- Total Deployed Personnel: {total} (Safe: {safe_cnt}, Warning: {warn_cnt}, Emergency: {emerg_cnt})\n"
            f"- Tactical Repeaters: Relay-01 (Ridge-Alpha)={r1_status}, Relay-02 (Ridge-Bravo)={r2_status}\n"
            f"- Personnel Telemetry:\n" + "\n".join(personnel_summary) + "\n"
            f"- Most Recent Transmission Events:\n" + ("\n".join(recent_events) if recent_events else "None") + "\n"
            f"NOTE: All values above are software simulated proof-of-concept data."
        )
        return context

    def generate_response(
        self,
        prompt: str,
        sim: Any = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        current_page: str = "Home Dashboard",
    ) -> Tuple[str, str]:
        """
        Processes a user query and returns (response_markdown, provider_badge).
        Provider badge indicates either 'Gemini API' or 'Local Demo Engine'.
        """
        clean_prompt = prompt.strip()
        if not clean_prompt:
            return "Please enter a question or select one of the suggested prompts.", "System Notice"

        # Construct situational context
        context_str = self.build_telemetry_context(sim, current_page)

        # 1. Try Live Gemini API if available
        if self.is_live_ai_available:
            try:
                system_instruction = (
                    "You are SURAKSHA AI, a tactical assistant for the SURAKSHA-NET Smart Soldier Protection, "
                    "Survival & Rescue System dashboard. You assist commanders, operators, and sponsors. "
                    "You answer questions in clear, professional English, or in Tenglish (Telugu-English mixed) "
                    "if the user asks in Tenglish. Always be concise, helpful, and safety-conscious. "
                    "CRITICAL SAFETY RULE: All sensor telemetry, vitals, and GPS readings are SIMULATED. "
                    "Never claim that real soldiers are deployed or that real medical/emergency services have been summoned. "
                    "Refer to the provided current simulated system state to answer questions accurately."
                )

                full_prompt = (
                    f"{system_instruction}\n\n"
                    f"{context_str}\n\n"
                    f"User Query: {clean_prompt}"
                )

                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                )

                if response and response.text:
                    return response.text.strip(), f"✨ {self.model_name} (Live AI)"
            except Exception as e:
                # Fall back gracefully on error (e.g. invalid key, quota, rate limit, network down)
                error_msg = str(e)
                # Fall through to local engine below with fallback badge
                local_reply = self._generate_local_reply(clean_prompt, sim, current_page)
                badge = "🤖 Demo Assistant (Rule-Based | Live API Error Fallback)"
                return f"{local_reply}\n\n> *[Notice: Live Gemini API encountered an issue ({error_msg[:60]}...). Showing verified local demo response.]*", badge

        # 2. Local Demo Assistant (Rule-based & Semantic Engine)
        local_reply = self._generate_local_reply(clean_prompt, sim, current_page)
        badge = "🤖 Demo Assistant (Rule-Based | No API Key Required)"
        return local_reply, badge

    def _generate_local_reply(self, prompt: str, sim: Any, current_page: str) -> str:
        """
        Intelligent rule-based local assistant supporting both English and
        Tenglish (Telugu-English mixed) queries with contextual simulation grounding.
        """
        p = prompt.lower()

        # Extract current simulation stats safely
        total_p = 3
        safe_p = 3
        emerg_p = 0
        warn_p = 0
        r1_up = True
        r2_up = True
        delta1_status = "SAFE"
        delta1_hr = 72
        delta1_temp = 36.7
        delta1_impact = 1.0

        if sim is not None and hasattr(sim, "soldiers"):
            total_p = len(sim.soldiers)
            safe_p = sum(1 for s in sim.soldiers.values() if getattr(s.get("status"), "value", str(s.get("status"))) == "SAFE")
            warn_p = sum(1 for s in sim.soldiers.values() if getattr(s.get("status"), "value", str(s.get("status"))) == "WARNING")
            emerg_p = sum(1 for s in sim.soldiers.values() if getattr(s.get("status"), "value", str(s.get("status"))) == "EMERGENCY")
            r1_up = sim.relay_status.get("RELAY-01", {}).get("operational", True)
            r2_up = sim.relay_status.get("RELAY-02", {}).get("operational", True)

            s1 = sim.soldiers.get("SOLDIER-01", {})
            if s1:
                delta1_status = getattr(s1.get("status"), "value", str(s1.get("status")))
                delta1_hr = s1.get("vitals", {}).heart_rate_bpm if hasattr(s1.get("vitals", {}), "heart_rate_bpm") else 72
                delta1_temp = s1.get("vitals", {}).body_temp_c if hasattr(s1.get("vitals", {}), "body_temp_c") else 36.7
                delta1_impact = s1.get("kinematics", {}).impact_g if hasattr(s1.get("kinematics", {}), "impact_g") else 1.0

        # Detect Tenglish query patterns
        is_tenglish = any(w in p for w in [
            "enti", "cheppu", "ela", "unnadu", "unnaru", "kavalenu", "ardham", "chesuko",
            "yenti", "kavali", "undi", "undhi", "emiti", "chesaru", "cheyali", "emaindi",
            "panchestundi", "evaru", "ippudu", "gurinchi"
        ])

        # 1. Personnel Status / Active Personnel
        if any(k in p for k in ["personnel", "soldier", "active status", "squad", "troops", "rajesh", "amit", "vikram"]) or ("status" in p and not "network" in p and not "relay" in p):
            if is_tenglish:
                return (
                    f"### 🎖️ Personnel Telemetry Status (Tenglish)\n"
                    f"Ippudu total **{total_p} simulated soldiers** patrol lo unnaru:\n"
                    f"- **Safe (Bhadramga)**: {safe_p}\n"
                    f"- **Warning (Hechharika)**: {warn_p}\n"
                    f"- **Emergency (Aapadha)**: {emerg_p}\n\n"
                    f"**Soldier Delta-1 (Sepoy Rajesh Kumar)** status ippudu: **{delta1_status}** "
                    f"(Heart Rate: {delta1_hr} BPM, Temp: {delta1_temp:.1f}°C, Impact: {delta1_impact:.2f}g).\n\n"
                    f"👉 Detail view kosam sidebar lo **'Personnel Monitoring'** section open cheyandi."
                )
            return (
                f"### 🎖️ Active Personnel Telemetry Status\n"
                f"Currently tracking **{total_p} simulated personnel**:\n"
                f"- **🟢 SAFE (Nominal)**: {safe_p} soldiers\n"
                f"- **🟡 WARNING (Caution)**: {warn_p} soldiers\n"
                f"- **🔴 EMERGENCY (Casualty)**: {emerg_p} soldiers\n\n"
                f"**Soldier Highlights**:\n"
                f"1. **Delta-1 (Sepoy Rajesh Kumar)**: State: `{delta1_status}` | HR: {delta1_hr} BPM | Temp: {delta1_temp:.1f}°C\n"
                f"2. **Delta-2 (Lance Naik Amit Singh)**: Valley Reconnaissance Unit\n"
                f"3. **Delta-3 (Havildar Vikram Thapa)**: Ridge Support Element\n\n"
                f"Navigate to the **Personnel Monitoring** tab from the sidebar for full vital telemetry graphs."
            )

        # 2. Emergency Alert / Latest Alert
        if any(k in p for k in ["alert", "emergency", "casualty", "accident", "blast", "fall", "hypothermia", "apada", "emaindi"]):
            if emerg_p > 0:
                if is_tenglish:
                    return (
                        f"### 🚨 Active Emergency Alert (Tenglish)\n"
                        f"**Jagratha!** System lo **{emerg_p} personnel EMERGENCY state** lo unnaru!\n"
                        f"- Soldier Delta-1 status: **{delta1_status}**\n"
                        f"- Impact force: **{delta1_impact:.2f}g** (Threshold: >4.5g blast shock)\n"
                        f"- Recommended Action: Ventane Emergency Simulation tab lo inspect chesi, medical triage instructions chudandi.\n\n"
                        f"> *Gurtunchukondi: Idi kevalam software simulation matrame.*"
                    )
                return (
                    f"### 🚨 Critical Emergency Alert Active!\n"
                    f"There are currently **{emerg_p} personnel in an EMERGENCY state**.\n"
                    f"- **Primary Casualty**: Delta-1 (Sepoy Rajesh Kumar)\n"
                    f"- **Trigger Severity**: Critical Impact / Manual SOS ({delta1_impact:.2f}g recorded)\n"
                    f"- **Recommended Tactical Action**: Dispatch forward medevac elements to simulated GPS coordinates. Prepare thermal stabilization kits.\n\n"
                    f"> *Reminder: This is an emulated simulation event.*"
                )
            else:
                if is_tenglish:
                    return (
                        f"### 🟢 Emergency Alert Status (Tenglish)\n"
                        f"Ippatiki system lo **elaanti critical emergencies levu**. Andaru soldiers `{safe_p}` safe state lo unnaru.\n"
                        f"Meeru emergency test cheyali anukunte, sidebar lo **'Emergency Simulation'** ki velli `Blast Shock` leda `SOS Trigger` button click cheyandi."
                    )
                return (
                    f"### 🟢 System Normal: No Active Emergencies\n"
                    f"All {safe_p} deployed personnel are currently operating within nominal baseline parameters.\n"
                    f"To test the triage system, navigate to the **Emergency Simulation** section and click **Trigger SOS** or **Blast Shock (>5g)**."
                )

        # 3. How SOS Works / SOS System
        if any(k in p for k in ["sos", "button", "help system", "panchestundi", "trigger"]):
            if is_tenglish:
                return (
                    f"### 🔘 SOS System Ela Panchestundi? (Tenglish)\n"
                    f"SURAKSHA-NET lo **SOS mechanism** 2 paddatulalo trigger avtundi:\n"
                    f"1. **Manual Tactile Push Button**: Soldier tanaku aapadha vachinappudu wearable meda unna Red SOS button nokkutaru.\n"
                    f"2. **Automatic Shock / Fall Detection**: MPU-6050 sensor blast shock (>4.5g) leda collapse detect chesinappudu automatic ga trigger avtundi.\n\n"
                    f"**Cancellation Grace Period**: Accident ga trigger aithe, soldier 10 seconds lo haptic buzz vachinappudu cancel cheyavachhu. Ledante emergency beacon base station ki transmit avtundi."
                )
            return (
                f"### 🔘 How the SURAKSHA-NET SOS System Operates\n"
                f"The SOS distress system provides both manual and automated protection:\n\n"
                f"1. **Manual Activation**: The soldier presses an IP67 sealed tactile pushbutton on their chest harness or wrist unit.\n"
                f"2. **Automated Impact Detection**: An on-node MPU-6050 accelerometer detects sudden concussive blast shock ($>4.5g$) or freefall followed by immobility.\n"
                f"3. **Local Alert & Haptic Pre-Alarm**: The wearable strobes a red LED and vibrates. A 10-second grace window allows conscious soldiers to cancel false alarms.\n"
                f"4. **Mesh Beaconing**: If not canceled, the node transmits emergency packets over 865–867 MHz LoRa via ridgeline repeaters to the base gateway."
            )

        # 4. Network Status / Relay Failover
        if any(k in p for k in ["network", "relay", "mesh", "lora", "repeater", "route", "failover", "signal", "rssi"]):
            r1_str = "🟢 ONLINE" if r1_up else "🔴 OFFLINE"
            r2_str = "🟢 ONLINE" if r2_up else "🔴 OFFLINE"
            if is_tenglish:
                return (
                    f"### 🌐 Mesh Network & Relay Status (Tenglish)\n"
                    f"Network repeater status ippudu:\n"
                    f"- **Relay-01 (Ridge-Repeater-Alpha)**: {r1_str}\n"
                    f"- **Relay-02 (Ridge-Repeater-Bravo Alternate)**: {r2_str}\n\n"
                    f"**Self-Healing Mesh**: Okaravela Relay-01 offline aipothe (jamming leda power drop valla), "
                    f"system automatic ga Relay-02 dwara traffic ni Base Station ki reroute chestundi! "
                    f"Sidebar lo **'Toggle Relay-01'** button click chesi idi live ga test cheyavachhu."
                )
            return (
                f"### 🌐 Mesh Network & Relay Repeater Telemetry\n"
                f"SURAKSHA-NET uses a decentralized sub-GHz mesh backhaul:\n\n"
                f"- **Relay-01 (Ridge-Repeater-Alpha, Primary)**: {r1_str}\n"
                f"- **Relay-02 (Ridge-Repeater-Bravo, Secondary Failover)**: {r2_str}\n"
                f"- **Operating Frequency**: 865–867 MHz (WPC License-Exempt in India)\n"
                f"- **Packet Deduplication**: 32-message ring buffer prevents broadcast storms.\n"
                f"- **Dynamic Failover**: If Relay-01 drops, packets automatically reroute through Relay-02 without data loss.\n\n"
                f"Check the **Network & Relay Status** tab for latency, RSSI, and hop counts."
            )

        # 5. How to Run Simulation / Emergency Simulation
        if any(k in p for k in ["run simulation", "simulate", "demo scenario", "test emergency", "ela run", "simulation"]):
            if is_tenglish:
                return (
                    f"### 🧪 Emergency Simulation Ela Run Cheyali? (Tenglish)\n"
                    f"Meeru dashboard lo simple ga simulations run cheyavachhu:\n"
                    f"1. Sidebar lo **'Emergency Simulation'** section ki vellandi.\n"
                    f"2. Ee buttons lo edo okati click cheyandi:\n"
                    f"   - **🚨 Trigger SOS Alert**: Manual distress call test chestundi.\n"
                    f"   - **💥 Blast Shock (>5g)**: High-impact blast triage ni trigger chestundi.\n"
                    f"   - **❄️ Hypothermia (<34°C)**: Extreme sub-zero body temperature alert.\n"
                    f"3. Taruvatha **'🔄 Reset Simulation'** click chesi nominal state ki return avvandi."
                )
            return (
                f"### 🧪 How to Execute an Emergency Simulation\n"
                f"Follow these steps to test the triage and failover capabilities:\n\n"
                f"1. Navigate to the **Emergency Simulation** section in the sidebar.\n"
                f"2. Select a simulated soldier tab (e.g. Delta-1).\n"
                f"3. Click any incident injection button:\n"
                f"   - **🚨 Trigger SOS Alert**: Simulates manual button press.\n"
                f"   - **💥 Blast Shock (>5g)**: Injects an explosive 5.6g shock wave.\n"
                f"   - **🤸 Fall & Collapse**: Simulates a fall with subsequent immobility.\n"
                f"   - **❄️ Hypothermia (<34°C)**: Triggers severe thermal drop.\n"
                f"4. Observe the emergency strobe, audio siren, and status change.\n"
                f"5. Click **Reset Simulation** to safely restore nominal conditions."
            )

        # 6. Explain the Dashboard / Navigation / Help
        if any(k in p for k in ["explain dashboard", "what is this", "enti idi", "guide", "help", "overview", "sections"]):
            if is_tenglish:
                return (
                    f"### 🛡️ SURAKSHA-NET Dashboard Overview (Tenglish)\n"
                    f"SURAKSHA-NET anedi **Smart Soldier Protection, Survival & Rescue System**.\n\n"
                    f"Dashboard lo unna 9 mukhyamaina sections:\n"
                    f"1. **Home Dashboard**: Quick squad summary and one-click actions.\n"
                    f"2. **Personnel Monitoring**: Prati soldier vitals (Heart rate, SpO2, Temp, Impact) graphs.\n"
                    f"3. **AI Assistant**: Naatho chat chesi queries adagavachhu (English & Tenglish).\n"
                    f"4. **Emergency Simulation**: Safe demo blast shocks, falls, and hypothermia triggers.\n"
                    f"5. **Network & Relay Status**: LoRa repeaters connectivity and mesh failover.\n"
                    f"6. **Map & Sector View**: Tactical GPS coordinate positions map meda.\n"
                    f"7. **Event Logs**: Prati alert timestamped history & CSV export.\n"
                    f"8. **Help & User Guide**: Step-by-step guided tour and troubleshooting.\n"
                    f"9. **Project Information**: Hardware BOM, roadmap, and sponsorship details."
                )
            return (
                f"### 🛡️ Welcome to SURAKSHA-NET Tactical Rescue Command\n"
                f"SURAKSHA-NET is a simulation-first IoT platform for military infantry and disaster rescue.\n\n"
                f"**Dashboard Sections Breakdown**:\n"
                f"- **1. Home Dashboard**: High-level command overview, squad status counters, and quick actions.\n"
                f"- **2. Personnel Monitoring**: In-depth physiological vitals (HR, SpO2, core temp) and kinematic shock.\n"
                f"- **3. AI Assistant**: WhatsApp/Gemini-style intelligent assistant for natural-language inquiries.\n"
                f"- **4. Emergency Simulation**: Safe, unvalidated scenario injection controls for demonstrations.\n"
                f"- **5. Network & Relay Status**: Tactical mesh repeater topology, RF health, and failover status.\n"
                f"- **6. Map & Sector View**: High-altitude geospatial GIS map tracking squad coordinates.\n"
                f"- **7. Event Logs**: Chronological mission audit trail with CSV download.\n"
                f"- **8. Help & User Guide**: Searchable documentation and an interactive step-by-step guided tour.\n"
                f"- **9. Project Information**: Hardware BOM in INR (₹), WPC regulations, and development roadmap."
            )

        # 7. Greetings / Pleasantries
        if any(k in p for k in ["hi", "hello", "hey", "namaste", "namaskaram", "ela unnav", "who are you"]):
            if is_tenglish:
                return (
                    f"Namaskaram! Nenu **SURAKSHA AI Assistant** ni. "
                    f"Nenu meeku dashboard navigate cheyadamlo, personnel telemetry explain cheyadamlo, "
                    f"mariyu emergency simulations run cheyadamlo sahayam cheyagalanu.\n\n"
                    f"Meeru English lo gaani, Tenglish (Telugu-English) lo gaani adagavachhu! "
                    f"Udaharanaki: *'Soldier 1 status enti?'* leda *'SOS ela panchestundi?'*"
                )
            return (
                f"Hello! I am **SURAKSHA AI**, your tactical command assistant. "
                f"I can explain telemetry readings, guide you through emergency simulations, "
                f"describe network mesh failovers, or help you navigate any section of this dashboard.\n\n"
                f"Feel free to ask questions in English or Tenglish, or click one of the suggested prompt pills below!"
            )

        # 8. Fallback / Default response
        if is_tenglish:
            return (
                f"Nenu me question ni ardam chesukogalanu: *\"{prompt}\"*.\n\n"
                f"Prastutaniki system **Normal Simulation Mode** lo undi. "
                f"Meeru kindi vishayala gurinchi adagavachhu:\n"
                f"- **'Soldier status cheppu'**: Active personnel vitals gurinchi.\n"
                f"- **'SOS ela panchestundi?'**: Emergency mechanism gurinchi.\n"
                f"- **'Relay network status enti?'**: Mesh repeaters gurinchi.\n"
                f"- **'Simulation ela run cheyali?'**: Demo incidents trigger cheyadaniki.\n\n"
                f"Leda sidebar lo **'Help & User Guide'** open chesi search cheyandi."
            )
        return (
            f"Thank you for your question: *\"{prompt}\"*.\n\n"
            f"Here is what you can explore in SURAKSHA-NET:\n"
            f"- **Personnel Vitals**: Check Soldier Delta-1, Delta-2, and Delta-3 telemetry in *Personnel Monitoring*.\n"
            f"- **Emergency Scenarios**: Test automated blast triage ($>4.5g$) in *Emergency Simulation*.\n"
            f"- **Self-Healing Mesh**: Inspect Ridge Repeaters Alpha & Bravo in *Network & Relay Status*.\n"
            f"- **Guided Walkthrough**: Open *Help & User Guide* in the sidebar for a guided step-by-step tour.\n\n"
            f"> *Note: You can configure a live Gemini API key via GEMINI_API_KEY for open-ended generative responses.*"
        )

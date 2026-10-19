"""
SURAKSHA-NET Tactical Rescue & Soldier Protection Command Dashboard
Upgraded with SURAKSHA AI Assistant (Gemini & Rule-Based Fallback), Help Center,
Interactive Guided Tour, and Responsive Multi-Section Navigation.

IMPORTANT DISCLAIMER:
Simulation-First Software Proof-of-Concept. All biomedical values, GPS positions,
impact forces, and RF propagation timings are emulated in software.
No clinical or ballistic validation has occurred.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone
import copy

from protocol import (
    SystemState,
    AlertType,
    THRESHOLDS,
)
from simulator import MeshSimulator
from ai_assistant import SurakshaAIAssistant
from help_center import render_help_center
from ui_components import (
    inject_custom_css,
    render_header,
    render_simulation_disclaimer,
    render_emergency_banner,
    render_floating_chat_pill,
    render_voice_support_widget,
)

# 1. Page Configuration (Wide layout, tactical icon)
st.set_page_config(
    page_title="SURAKSHA-NET | Smart Soldier Rescue Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom modern tactical CSS
inject_custom_css()

# 2. Session State Initialization
if "simulator" not in st.session_state:
    st.session_state.simulator = MeshSimulator()

if "ai_assistant" not in st.session_state:
    st.session_state.ai_assistant = SurakshaAIAssistant()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Namaskaram & Welcome to **SURAKSHA AI**! 🛡️\n\n"
                "I am your tactical command assistant. I can explain live soldier telemetry, "
                "guide you through emergency simulations, describe network mesh failovers, "
                "or answer project architecture questions.\n\n"
                "You can ask me questions in **English** or **Tenglish** (Telugu-English mixed)!\n\n"
                "Try asking:\n"
                "- *'Explain the dashboard.'*\n"
                "- *'Show active personnel status.'*\n"
                "- *'Soldier 1 status cheppu'* (Tenglish)\n"
                "- *'How does the SOS system work?'*"
            ),
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M UTC"),
            "badge": "System Welcome",
        }
    ]

if "current_page" not in st.session_state:
    st.session_state.current_page = "1. Home Dashboard"

sim: MeshSimulator = st.session_state.simulator
ai: SurakshaAIAssistant = st.session_state.ai_assistant

# 3. Sidebar Navigation (Exact 9 Sections)
NAV_SECTIONS = [
    "1. Home Dashboard",
    "2. Personnel Monitoring",
    "3. AI Assistant",
    "4. Emergency Simulation",
    "5. Network & Relay Status",
    "6. Map & Sector View",
    "7. Event Logs",
    "8. Help & User Guide",
    "9. Project Information",
]

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("SURAKSHA-NET")
    st.caption("Tactical Rescue Command (TBOC-01)")

    st.markdown("---")
    st.subheader("🧭 Command Navigation")

    # Sidebar Radio Navigation
    selected_page = st.radio(
        "Select Section:",
        NAV_SECTIONS,
        index=NAV_SECTIONS.index(st.session_state.current_page) if st.session_state.current_page in NAV_SECTIONS else 0,
        key="nav_radio"
    )
    st.session_state.current_page = selected_page

    st.markdown("---")
    st.subheader("🌐 Quick Relay Controls")
    r1_up = sim.relay_status["RELAY-01"]["operational"]
    r2_up = sim.relay_status["RELAY-02"]["operational"]

    c_r1, c_r2 = st.columns(2)
    with c_r1:
        st.caption(f"**Relay 01**: {'🟢 ON' if r1_up else '🔴 OFF'}")
        if st.button("Toggle R1", key="side_btn_r1", use_container_width=True):
            sim.toggle_relay_failure("RELAY-01")
            st.rerun()

    with c_r2:
        st.caption(f"**Relay 02**: {'🟢 ON' if r2_up else '🔴 OFF'}")
        if st.button("Toggle R2", key="side_btn_r2", use_container_width=True):
            sim.toggle_relay_failure("RELAY-02")
            st.rerun()

    st.markdown("---")
    # Live Vitals Jitter toggle
    auto_jitter = st.checkbox("Live Sensor Jitter (1s Stream)", value=True, help="Simulates subtle human heart rate and temperature drift")
    if auto_jitter:
        sim.step_simulation()

    if st.button("🔄 Global Refresh", use_container_width=True):
        st.rerun()

    st.markdown("---")
    # AI Engine Badge
    if ai.is_live_ai_available:
        st.success(f"✨ AI Model: {ai.model_name}")
    else:
        st.info("🤖 AI Model: Local Rule-Based Engine (No API Key Required)")

    st.caption("SURAKSHA-NET v2.0-AI | Zero-Cost POC")

# 4. Global Header and Banners
render_header("SURAKSHA-NET", "Tactical Soldier Protection, Automated Casualty Triage & Rescue Command")
render_simulation_disclaimer()

# Count active statuses
total_soldiers = len(sim.soldiers)
emergency_count = sum(1 for s in sim.soldiers.values() if getattr(s.get("status"), "value", str(s.get("status"))) == "EMERGENCY")
warning_count = sum(1 for s in sim.soldiers.values() if getattr(s.get("status"), "value", str(s.get("status"))) == "WARNING")
safe_count = sum(1 for s in sim.soldiers.values() if getattr(s.get("status"), "value", str(s.get("status"))) == "SAFE")
relays_active = sum(1 for r in sim.relay_status.values() if r["operational"])

# Persistent Emergency Banner across all pages if casualties active
render_emergency_banner(emergency_count)

# Floating chat button at bottom-right
render_floating_chat_pill()

# ==============================================================================
# SECTION 1: HOME DASHBOARD
# ==============================================================================
if st.session_state.current_page == "1. Home Dashboard":
    st.subheader("📊 Squad Overview & Tactical Readiness")
    st.caption("Real-time summary of deployed personnel, network repeaters, and tactical quick actions.")

    # 5 Top Tactical Summary Metrics
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    with col_m1:
        st.metric("Total Deployed Units", f"{total_soldiers} Active", help="Simulated wearable nodes deployed on mountain patrol")
    with col_m2:
        st.metric("Safe Patrol (Nominal)", f"{safe_count}", delta=f"{safe_count}/{total_soldiers}", delta_color="normal")
    with col_m3:
        st.metric("Warning State", f"{warning_count}", delta=f"{warning_count} Alert" if warning_count > 0 else "0", delta_color="inverse")
    with col_m4:
        st.metric("EMERGENCY CASUALTY", f"{emergency_count}", delta=f"{emergency_count} CRITICAL" if emergency_count > 0 else "0", delta_color="inverse")
    with col_m5:
        st.metric("Relay Mesh Nodes", f"{relays_active}/2 Active", delta="Degraded" if relays_active < 2 else "Optimal", delta_color="normal" if relays_active == 2 else "inverse")

    st.markdown("---")

    # Quick Action Area
    st.markdown("### ⚡ Tactical Quick Actions")
    st.caption("Frequently used operations for rapid deployment and mission assessment:")

    qa_col1, qa_col2, qa_col3, qa_col4, qa_col5, qa_col6 = st.columns(6)
    with qa_col1:
        if st.button("👥 View Personnel", use_container_width=True, help="Jump to detailed vital signs"):
            st.session_state.current_page = "2. Personnel Monitoring"
            st.rerun()

    with qa_col2:
        if st.button("🧪 Run Safe Demo", use_container_width=True, help="Restore nominal safe patrol conditions"):
            sim.run_safe_scenario()
            st.success("Safe demo scenario applied: All personnel reporting SAFE.")
            st.rerun()

    with qa_col3:
        if st.button("🤖 Open AI Assistant", use_container_width=True, help="Chat with SURAKSHA AI in English or Tenglish"):
            st.session_state.current_page = "3. AI Assistant"
            st.rerun()

    with qa_col4:
        if st.button("📜 View Recent Events", use_container_width=True, help="Inspect event logs"):
            st.session_state.current_page = "7. Event Logs"
            st.rerun()

    with qa_col5:
        if st.button("📖 Open User Guide", use_container_width=True, help="Search help & start guided tour"):
            st.session_state.current_page = "8. Help & User Guide"
            st.rerun()

    with qa_col6:
        # Export Demo Logs directly
        if sim.event_log:
            df_quick_log = pd.DataFrame(sim.event_log)
            csv_data = df_quick_log.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Logs",
                data=csv_data,
                file_name=f"suraksha_demo_logs_{datetime.now(timezone.utc).strftime('%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.button("📥 Export Logs", disabled=True, use_container_width=True)

    st.markdown("---")

    # Squad Personnel Cards Preview
    st.markdown("### 🎖️ Deployed Personnel Status Cards")
    s_cols = st.columns(3)
    for idx, (s_id, s) in enumerate(sim.soldiers.items()):
        with s_cols[idx]:
            st_val = s["status"].value if hasattr(s["status"], "value") else str(s["status"])
            badge_class = "badge-safe" if st_val == "SAFE" else ("badge-warning" if st_val == "WARNING" else "badge-emergency")

            st.markdown(f"""
            <div class="tactical-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size: 16px; font-weight: 700; color:#ffffff;">{s['callsign']}</span>
                    <span class="{badge_class}">{st_val}</span>
                </div>
                <div style="font-size:13px; color:#8b949e; margin: 4px 0 10px 0;">{s['name']} — {s['unit']}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size:13px;">
                    <div>💓 HR: <strong>{s['vitals'].heart_rate_bpm} BPM</strong></div>
                    <div>🫁 SpO2: <strong>{s['vitals'].spo2_percent}%</strong></div>
                    <div>🌡️ Temp: <strong>{s['vitals'].body_temp_c:.1f}°C</strong></div>
                    <div>💥 Shock: <strong>{s['kinematics'].impact_g:.2f}g</strong></div>
                </div>
                <div style="margin-top: 10px; font-size: 12px; color:#58a6ff;">
                    📍 Alt: {s['gps'].altitude_m:.0f}m | Bat: {s['power'].battery_pct}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Inspect {s['callsign']} 🔍", key=f"btn_inspect_{s_id}", use_container_width=True):
                st.session_state.current_page = "2. Personnel Monitoring"
                st.rerun()

    st.markdown("---")

    # High Altitude Map Preview
    st.markdown("### 🗺️ Tactical Deployment Sector Map Preview")
    map_preview_data = []
    for s_id, s in sim.soldiers.items():
        st_val = s["status"].value if hasattr(s["status"], "value") else str(s["status"])
        map_preview_data.append({
            "name": f"{s['callsign']} - {s['name']} ({st_val})",
            "lat": s["gps"].latitude,
            "lon": s["gps"].longitude,
        })
    map_preview_data.append({"name": "Relay-01 (Ridge-Alpha)", "lat": 35.0000, "lon": 76.8000})
    map_preview_data.append({"name": "Relay-02 (Ridge-Bravo)", "lat": 34.8000, "lon": 76.4000})
    map_preview_data.append({"name": "Base Command HQ", "lat": 34.2000, "lon": 76.0000})

    df_map_preview = pd.DataFrame(map_preview_data)
    st.map(df_map_preview, latitude="lat", longitude="lon", zoom=7)


# ==============================================================================
# SECTION 2: PERSONNEL MONITORING
# ==============================================================================
elif st.session_state.current_page == "2. Personnel Monitoring":
    st.subheader("👥 Personnel Telemetry & Real-Time Biometrics")
    st.caption("Detailed physiological, kinematic, and battery telemetry for each deployed infantry unit.")

    soldier_tabs = st.tabs([
        f"🔴 {sim.soldiers['SOLDIER-01']['callsign']} (EMERGENCY)" if getattr(sim.soldiers['SOLDIER-01']['status'], "value", str(sim.soldiers['SOLDIER-01']['status'])) == "EMERGENCY" else f"🟢 {sim.soldiers['SOLDIER-01']['callsign']} ({sim.soldiers['SOLDIER-01']['name']})",
        f"🟡 {sim.soldiers['SOLDIER-02']['callsign']} (WARNING)" if getattr(sim.soldiers['SOLDIER-02']['status'], "value", str(sim.soldiers['SOLDIER-02']['status'])) == "WARNING" else f"🟢 {sim.soldiers['SOLDIER-02']['callsign']} ({sim.soldiers['SOLDIER-02']['name']})",
        f"🟢 {sim.soldiers['SOLDIER-03']['callsign']} ({sim.soldiers['SOLDIER-03']['name']})",
    ])

    for i, (s_id, tab) in enumerate(zip(["SOLDIER-01", "SOLDIER-02", "SOLDIER-03"], soldier_tabs)):
        soldier = sim.soldiers[s_id]
        with tab:
            c_left, c_mid, c_right = st.columns([1.2, 1.8, 1.2])

            with c_left:
                st.markdown(f"### {soldier['name']}")
                st.caption(f"Callsign: **{soldier['callsign']}** | ID: `{soldier['id']}`")
                st.caption(f"Role: {soldier['unit']}")

                st_val = soldier['status'].value if hasattr(soldier['status'], "value") else str(soldier['status'])
                badge_class = "badge-safe" if st_val == "SAFE" else ("badge-warning" if st_val == "WARNING" else "badge-emergency")
                st.markdown(f'<div class="{badge_class}">STATUS: {st_val}</div>', unsafe_allow_html=True)

                st.markdown(f"**Alert Classification**: `{soldier['alert_type'].value if hasattr(soldier['alert_type'], 'value') else soldier['alert_type']}`")
                st.markdown(f"**Battery Reserve**: {soldier['power'].battery_pct}% ({soldier['power'].voltage_v:.2f}V)")
                st.progress(soldier['power'].battery_pct / 100.0)

            with c_mid:
                st.markdown("#### Physiological & Kinematic Vitals")
                v1, v2, v3 = st.columns(3)
                with v1:
                    hr = soldier['vitals'].heart_rate_bpm
                    st.metric(
                        "Heart Rate (BPM)",
                        f"{hr} BPM",
                        delta=f"{hr-75:+d} bpm",
                        delta_color="normal" if 50 <= hr <= 120 else "inverse",
                        help="Beats per minute. Emergency if <45 or >160"
                    )
                    impact = soldier['kinematics'].impact_g
                    st.metric(
                        "Impact Force (g-force)",
                        f"{impact:.2f} g",
                        delta=f"Threshold: {THRESHOLDS['IMPACT_THRESHOLD_G']}g",
                        delta_color="inverse" if impact >= THRESHOLDS['IMPACT_THRESHOLD_G'] else "normal",
                        help="Instantaneous acceleration shock vector"
                    )

                with v2:
                    spo2 = soldier['vitals'].spo2_percent
                    st.metric(
                        "Oxygen (SpO2 %)",
                        f"{spo2} %",
                        delta=f"{spo2-98:+d}%",
                        delta_color="normal" if spo2 >= 90 else "inverse",
                        help="Blood oxygen saturation. Hypoxia if <88%"
                    )
                    fall_flag = "DETECTED" if soldier['kinematics'].fall_detected else "NONE"
                    st.metric(
                        "Fall & Posture",
                        fall_flag,
                        delta="Immobile" if soldier['kinematics'].is_immobile else "Active Movement",
                        delta_color="inverse" if soldier['kinematics'].fall_detected else "normal",
                        help="Freefall followed by sudden shock and immobility"
                    )

                with v3:
                    temp = soldier['vitals'].body_temp_c
                    st.metric(
                        "Body Temp (°C)",
                        f"{temp:.1f} °C",
                        delta=f"{temp-36.8:+.1f}°C",
                        delta_color="normal" if 35.5 <= temp <= 38.0 else "inverse",
                        help="Core/skin temperature. Hypothermia if <35.0°C"
                    )
                    gps = soldier['gps']
                    st.metric(
                        "Tactical Altitude",
                        f"{gps.altitude_m:.0f} m",
                        help=f"Coordinates: {gps.latitude:.4f}°N, {gps.longitude:.4f}°E"
                    )

                route, hops, rssi, backup, delivery = sim.determine_route(s_id)
                route_str = " ➔ ".join(route)
                badge_note = " (⚡ FAILOVER PATH)" if backup else ""
                st.info(f"**RF Mesh Route**: `{route_str}`{badge_note} | **Signal**: `{rssi} dBm` | **Hops**: `{hops}`")

            with c_right:
                st.markdown("#### Tactical Demo Actions")
                b_a, b_b = st.columns(2)
                with b_a:
                    if st.button("🚨 SOS Alert", key=f"p_sos_{s_id}", use_container_width=True):
                        sim.trigger_sos(s_id)
                        st.rerun()
                    if st.button("💥 Blast Shock", key=f"p_blast_{s_id}", use_container_width=True):
                        sim.trigger_impact(s_id, impact_g=5.5)
                        st.rerun()
                    if st.button("🤸 Fall Event", key=f"p_fall_{s_id}", use_container_width=True):
                        sim.trigger_fall(s_id, immobile=True)
                        st.rerun()

                with b_b:
                    if st.button("❄️ Cold Stress", key=f"p_cold_{s_id}", use_container_width=True):
                        sim.trigger_temp_warning(s_id, temp_c=33.5)
                        st.rerun()
                    if st.button("💓 Tachycardia", key=f"p_tachy_{s_id}", use_container_width=True):
                        sim.trigger_cardiac_warning(s_id, hr=165, spo2=87)
                        st.rerun()
                    if st.button("🔄 Reset Unit", key=f"p_rst_{s_id}", use_container_width=True):
                        sim.reset_soldier(s_id)
                        st.rerun()


# ==============================================================================
# SECTION 3: AI ASSISTANT ("Ask SURAKSHA AI")
# ==============================================================================
elif st.session_state.current_page == "3. AI Assistant":
    st.subheader("🤖 Ask SURAKSHA AI — Tactical Chat Assistant")
    st.caption("Ask questions in English or Tenglish (Telugu-English mixed) about telemetry, emergency alerts, or network routing.")

    # Status indicator
    ai_status_col1, ai_status_col2 = st.columns([3, 1])
    with ai_status_col1:
        if ai.is_live_ai_available:
            st.success(f"✨ Live Gemini API Connected ({ai.model_name}) | Fully contextualized to current telemetry.")
        else:
            st.info("🤖 Operating in Local Demo Mode (Rule-Based & Semantic Engine). No API key required!")
    with ai_status_col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": "Conversation reset. How can I assist you with SURAKSHA-NET?",
                    "timestamp": datetime.now(timezone.utc).strftime("%H:%M UTC"),
                    "badge": "System",
                }
            ]
            st.rerun()

    # Browser Web Speech API Voice Widget
    with st.expander("🎙️ Voice Assistant Controls (Speak / Listen)", expanded=False):
        render_voice_support_widget()

    # Suggested Prompts Chips
    st.markdown("**Suggested Questions** (Click to ask immediately):")
    p_col1, p_col2, p_col3 = st.columns(3)
    prompt_selected = None

    with p_col1:
        if st.button("📌 Explain the dashboard.", use_container_width=True):
            prompt_selected = "Explain the dashboard."
        if st.button("🎖️ Show active personnel status.", use_container_width=True):
            prompt_selected = "Show active personnel status."

    with p_col2:
        if st.button("🚨 Explain the latest emergency alert.", use_container_width=True):
            prompt_selected = "Explain the latest emergency alert."
        if st.button("🔘 How does the SOS system work?", use_container_width=True):
            prompt_selected = "How does the SOS system work?"

    with p_col3:
        if st.button("🧪 How do I run an emergency simulation?", use_container_width=True):
            prompt_selected = "How do I run an emergency simulation?"
        if st.button("🌐 Explain the network status.", use_container_width=True):
            prompt_selected = "Explain the network status."

    st.markdown("---")

    # Render Chat History
    chat_box = st.container()
    with chat_box:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.chat_history:
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            ts = msg.get("timestamp", "")
            badge = msg.get("badge", "SURAKSHA AI")

            if role == "user":
                st.markdown(f"""
                <div class="chat-bubble-user">
                    <div style="font-weight: 600; margin-bottom: 4px; color: #7ee787;">👤 You</div>
                    <div>{content.replace(chr(10), '<br/>')}</div>
                    <div class="chat-meta" style="justify-content: flex-end;">{ts}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-bubble-assistant">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                        <span style="font-weight: 700; color: #58a6ff;">🛡️ SURAKSHA AI</span>
                        <span class="chat-ai-badge">{badge}</span>
                    </div>
                    <div style="color: #e6edf3;">{content.replace(chr(10), '<br/>')}</div>
                    <div class="chat-meta">
                        <span>{ts}</span>
                        <span style="font-size: 10px; color:#8b949e;">Verified Demo Telemetry</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat Input Box
    user_query = st.chat_input("Ask SURAKSHA AI in English or Tenglish (e.g. 'Soldier 1 status cheppu', 'How does SOS work?')...")
    active_query = prompt_selected or user_query

    if active_query:
        now_ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        # Record user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": active_query,
            "timestamp": now_ts,
        })

        # Generate Assistant response with typing simulation
        with st.spinner("SURAKSHA AI analyzing tactical telemetry..."):
            reply_text, badge_label = ai.generate_response(
                prompt=active_query,
                sim=sim,
                chat_history=st.session_state.chat_history,
                current_page=st.session_state.current_page,
            )

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply_text,
            "timestamp": now_ts,
            "badge": badge_label,
        })
        st.rerun()


# ==============================================================================
# SECTION 4: EMERGENCY SIMULATION
# ==============================================================================
elif st.session_state.current_page == "4. Emergency Simulation":
    st.subheader("🧪 Emergency Simulation Control Center")
    st.caption("Safely evaluate triage thresholds, blast impacts, and failover routing without physical hardware.")

    # Obvious simulation banner
    render_simulation_disclaimer()

    # Controls container
    st.markdown("### 🎯 Trigger Simulated Incident")
    st.write("Select a soldier and simulate a tactical or environmental trauma event:")

    target_soldier_id = st.selectbox(
        "Select Target Personnel for Simulation:",
        options=["SOLDIER-01", "SOLDIER-02", "SOLDIER-03"],
        format_func=lambda x: f"{sim.soldiers[x]['callsign']} — {sim.soldiers[x]['name']} ({sim.soldiers[x]['unit']})",
        key="sim_target_select"
    )

    col_sim1, col_sim2, col_sim3, col_sim4, col_sim5 = st.columns(5)
    with col_sim1:
        if st.button("🚨 Simulated SOS", use_container_width=True, help="Simulate soldier pressing tactile emergency switch"):
            sim.trigger_sos(target_soldier_id)
            st.success(f"SOS triggered for {target_soldier_id}!")
            st.rerun()

    with col_sim2:
        if st.button("💥 Blast Shock (>5g)", use_container_width=True, help="Simulate concussive explosive blast (5.6g)"):
            sim.trigger_impact(target_soldier_id, impact_g=5.6)
            st.success(f"Concussive blast shock injected on {target_soldier_id}!")
            st.rerun()

    with col_sim3:
        if st.button("🤸 Fall & Collapse", use_container_width=True, help="Simulate freefall followed by immobility"):
            sim.trigger_fall(target_soldier_id, immobile=True)
            st.success(f"Fall and immobility event triggered on {target_soldier_id}!")
            st.rerun()

    with col_sim4:
        if st.button("❄️ Hypothermia (<34°C)", use_container_width=True, help="Simulate severe sub-zero thermal collapse"):
            sim.trigger_temp_warning(target_soldier_id, temp_c=33.6)
            st.warning(f"Hypothermia alert injected on {target_soldier_id}!")
            st.rerun()

    with col_sim5:
        # Reset Simulation with confirmation
        if st.button("🔄 Reset Simulation", use_container_width=True, help="Restore nominal safe patrol conditions"):
            sim.run_safe_scenario()
            st.success("Simulation reset: All personnel restored to SAFE status.")
            st.rerun()

    st.markdown("---")

    # Detailed Incident Event Card for latest event
    st.markdown("### 📋 Latest Simulated Incident Summary")
    if sim.event_log:
        latest = sim.event_log[0]
        st.markdown(f"""
        <div class="tactical-card" style="border-left: 6px solid {'#f85149' if latest.get('severity') == 'CRITICAL' else ('#d29922' if latest.get('severity') == 'WARNING' else '#3fb950')};">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <span style="background:#21262d; border: 1px solid #30363d; padding:2px 8px; border-radius:6px; font-size:11px; color:#58a6ff;">
                        {latest.get('sim_badge', 'SIMULATED')}
                    </span>
                    <span style="font-weight:700; font-size:16px; margin-left: 8px; color:#ffffff;">
                        {latest.get('event_id', 'EVT-0000')}: {latest.get('alert_type')}
                    </span>
                </div>
                <div style="font-size:12px; color:#8b949e;">{latest.get('timestamp')}</div>
            </div>
            <div style="margin-top: 10px; font-size:14px; line-height: 1.6;">
                <div>👤 <strong>Personnel</strong>: {latest.get('personnel')} ({latest.get('origin_id')})</div>
                <div>📍 <strong>Last-Known Location</strong>: {latest.get('location', 'High-Altitude Ridge Grid')}</div>
                <div>⚠️ <strong>Severity Level</strong>: <span style="color:{'#ff7b72' if latest.get('severity') == 'CRITICAL' else '#d29922'}; font-weight:700;">{latest.get('severity')}</span></div>
                <div>🌐 <strong>Route Path</strong>: `{latest.get('route')}` ({latest.get('delivery')})</div>
                <div>🩺 <strong>Recommended Next Step</strong>: {latest.get('recommended_step')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No events recorded yet. Run a simulation above.")


# ==============================================================================
# SECTION 5: NETWORK & RELAY STATUS
# ==============================================================================
elif st.session_state.current_page == "5. Network & Relay Status":
    st.subheader("🌐 Mesh Network & Tactical Relay Telemetry")
    st.caption("Self-healing decentralized LoRa mesh backhaul operating in the Indian 865–867 MHz WPC band.")

    r_col1, r_col2 = st.columns(2)

    with r_col1:
        r1 = sim.relay_status["RELAY-01"]
        is_r1_on = r1["operational"]
        st.markdown(f"""
        <div class="tactical-card" style="border-left: 6px solid {'#3fb950' if is_r1_on else '#f85149'};">
            <h3>RELAY-01: {r1['name']}</h3>
            <p style="color:#8b949e;">📍 Location: {r1['location']}</p>
            <p>Status: <strong>{'🟢 OPERATIONAL / ACTIVE' if is_r1_on else '🔴 OFFLINE / JAMMED'}</strong></p>
            <p>Frequency: <code>866.1 MHz (125 kHz BW, SF10)</code></p>
            <p>Transmit Power: <code>+20 dBm (100mW)</code></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{'Disable' if is_r1_on else 'Restore'} Relay-01", key="btn_page_r1", use_container_width=True):
            sim.toggle_relay_failure("RELAY-01")
            st.rerun()

    with r_col2:
        r2 = sim.relay_status["RELAY-02"]
        is_r2_on = r2["operational"]
        st.markdown(f"""
        <div class="tactical-card" style="border-left: 6px solid {'#3fb950' if is_r2_on else '#f85149'};">
            <h3>RELAY-02: {r2['name']}</h3>
            <p style="color:#8b949e;">📍 Location: {r2['location']}</p>
            <p>Status: <strong>{'🟢 OPERATIONAL / ACTIVE' if is_r2_on else '🔴 OFFLINE / JAMMED'}</strong></p>
            <p>Frequency: <code>866.5 MHz (125 kHz BW, SF10)</code></p>
            <p>Role: <code>Automatic Mesh Failover Path</code></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{'Disable' if is_r2_on else 'Restore'} Relay-02", key="btn_page_r2", use_container_width=True):
            sim.toggle_relay_failure("RELAY-02")
            st.rerun()

    st.markdown("---")

    # Routing Paths Breakdown
    st.markdown("### 📡 Active Squad RF Routing Topology")
    route_rows = []
    for s_id, s in sim.soldiers.items():
        route, hops, rssi, backup, delivery = sim.determine_route(s_id)
        route_rows.append({
            "Callsign": s["callsign"],
            "Personnel": s["name"],
            "Active Path": " ➔ ".join(route),
            "Hop Count": hops,
            "Signal (RSSI)": f"{rssi} dBm",
            "Path Type": "⚡ Backup Failover" if backup else "Primary Mesh",
            "Delivery Status": delivery,
        })
    df_routes = pd.DataFrame(route_rows)
    st.dataframe(df_routes, hide_index=True, use_container_width=True)


# ==============================================================================
# SECTION 6: MAP & SECTOR VIEW
# ==============================================================================
elif st.session_state.current_page == "6. Map & Sector View":
    st.subheader("🗺️ High-Altitude Tactical Deployment GIS Map")
    st.caption("Simulated coordinates representing high-altitude forward patrol deployment (Ladakh/Kargil Theater).")

    map_c1, map_c2 = st.columns([2.5, 1])

    with map_c1:
        map_points = []
        for s_id, s in sim.soldiers.items():
            st_val = s["status"].value if hasattr(s["status"], "value") else str(s["status"])
            map_points.append({
                "Name": f"{s['callsign']} ({s['name']}) - {st_val}",
                "lat": s["gps"].latitude,
                "lon": s["gps"].longitude,
            })
        map_points.append({"Name": "RELAY-01 (Ridge-Alpha)", "lat": 35.0000, "lon": 76.8000})
        map_points.append({"Name": "RELAY-02 (Ridge-Bravo)", "lat": 34.8000, "lon": 76.4000})
        map_points.append({"Name": "Base HQ (Gateway)", "lat": 34.2000, "lon": 76.0000})

        df_full_map = pd.DataFrame(map_points)
        st.map(df_full_map, latitude="lat", longitude="lon", zoom=7)

    with map_c2:
        st.markdown("#### Sector Manifest")
        manifest_data = []
        for s_id, s in sim.soldiers.items():
            g = s["gps"]
            manifest_data.append({
                "Node": s["callsign"],
                "Lat": f"{g.latitude:.4f}°",
                "Lon": f"{g.longitude:.4f}°",
                "Alt": f"{g.altitude_m:.0f}m",
            })
        st.dataframe(pd.DataFrame(manifest_data), hide_index=True, use_container_width=True)
        st.caption("Sector elevation ranges from 3,280m to 5,420m AMSL.")


# ==============================================================================
# SECTION 7: EVENT LOGS
# ==============================================================================
elif st.session_state.current_page == "7. Event Logs":
    st.subheader("📜 Chronological Mission Event Audit Log")
    st.caption("Tamper-evident, timestamped log of all telemetry frames, alert triggers, and mesh failovers.")

    if sim.event_log:
        df_log = pd.DataFrame(sim.event_log)

        # Filter controls
        filter_col1, filter_col2 = st.columns([2, 1])
        with filter_col1:
            severity_filter = st.selectbox(
                "Filter by Severity:",
                options=["ALL", "CRITICAL", "WARNING", "NORMAL"],
                key="log_filter_select"
            )

        if severity_filter != "ALL":
            filtered_df = df_log[df_log["severity"] == severity_filter]
        else:
            filtered_df = df_log

        st.dataframe(
            filtered_df[["event_id", "timestamp", "origin_id", "personnel", "severity", "alert_type", "location", "recommended_step", "route", "delivery"]],
            hide_index=True,
            use_container_width=True,
        )

        # Export Button
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Incident Log (CSV)",
            data=csv_bytes,
            file_name=f"suraksha_incident_log_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No mission events logged yet.")


# ==============================================================================
# SECTION 8: HELP & USER GUIDE
# ==============================================================================
elif st.session_state.current_page == "8. Help & User Guide":
    render_help_center()


# ==============================================================================
# SECTION 9: PROJECT INFORMATION
# ==============================================================================
elif st.session_state.current_page == "9. Project Information":
    st.subheader("🛡️ Project Architecture & Engineering Specifications")
    st.caption("Detailed overview of technical specifications, hardware Bill of Materials, and development roadmap.")

    tab_arch, tab_bom, tab_road, tab_ip = st.tabs([
        "System Architecture",
        "Hardware BOM (INR ₹)",
        "Staged Roadmap",
        "IP & Compliance"
    ])

    with tab_arch:
        st.markdown("""
        ### Multi-Tier Architecture Overview
        1. **Wearable Tactical Unit**: Dual-core ESP32 (240MHz), MPU-6050 (6-DOF IMU), DHT22 temperature sensor, SSD1306 OLED, tactile SOS switch, and haptic buzzer.
        2. **Autonomous Tactical Relays**: Solar-buffered ridgeline repeaters executing an in-memory 32-message ring buffer to eliminate duplicate broadcast storms.
        3. **Tactical Gateway Base**: Dedicated receiver with 90dB siren, red casualty strobe, and USB bridge to this command dashboard.
        4. **Command Dashboard**: Python/Streamlit air-gapped interface with integrated Gemini AI assistant.
        """)

    with tab_bom:
        st.markdown("""
        ### Indicative Hardware BOM Breakdown (INR ₹)
        - **Soldier Wearable Unit (Core Prototype)**: **₹2,510**
        - **Soldier Wearable Unit (Fully Loaded with MAX30102 & GPS)**: **₹4,580**
        - **Autonomous Solar Relay Node**: **₹9,350**
        - **Base Station Gateway Console**: **₹1,765**
        - **Volume Production Projection (1,000+ Units)**: **₹890 – ₹1,280 per wearable**
        
        *Sourcing: Readily available through Indian electronic distributors (Robu.in, Tanotis, Mouser India).*
        """)

    with tab_road:
        st.markdown("""
        ### 4-Stage Development Roadmap
        - **Phase 1 (Completed)**: Zero-Cost Software Simulation POC (₹0 budget).
        - **Phase 2 (Months 1–3)**: Breadboard & Benchtop Integration + 2.5 km RF Range Trials (**₹50,000 budget**).
        - **Phase 3 (Months 4–7)**: 4-Layer SMT PCB Fabrication + IP68 Enclosures + Squad Field Trials (**₹2,50,000 budget**).
        - **Phase 4 (Months 8–12)**: MIL-STD-810H Qualification + WPC ETA Certification + Military Pilot Trials (**₹12,00,000 budget**).
        """)

    with tab_ip:
        st.markdown("""
        ### Intellectual Property & Regulatory Compliance
        - **Indian WPC Compliance**: Operating in the 865–867 MHz license-exempt band under GSR 564(E) regulations (Max radiated power: 1 Watt / +30 dBm).
        - **Defense Patent Considerations**: Section 35 of the Indian Patents Act, 1970 (Secrecy Directions for Defense Inventions).
        - **Open Source Boundaries**: Apache 2.0 / MIT licensing for software proof of concept; proprietary trade secret algorithms for production SMT firmware.
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #8b949e; font-size: 13px;">
    <strong>SURAKSHA-NET Defense Tech Prototype</strong> | Developed by Autonomous Engineering Team<br/>
    Simulation-First Architecture | Compatible with Wokwi ESP32 & Arduino Core
</div>
""", unsafe_allow_html=True)

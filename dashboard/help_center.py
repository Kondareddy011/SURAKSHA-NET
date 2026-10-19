"""
SURAKSHA-NET Help Assistant & Interactive Knowledge Base
Provides searchable documentation cards and an interactive step-by-step guided tour.
"""

import streamlit as st
import html
from typing import Dict, List, Any


HELP_TOPICS = [
    {
        "id": "overview",
        "title": "1. Dashboard Overview & Concept",
        "category": "Getting Started",
        "summary": "What is SURAKSHA-NET and how does the tactical rescue system work?",
        "content": """
        **SURAKSHA-NET** is an IoT-enabled Smart Soldier Protection, Survival, and Automated Rescue System.
        
        It is designed for military infantry and disaster relief teams operating in contested, non-networked environments (like high-altitude mountain sectors) where commercial 4G/5G cellular coverage does not exist.
        
        The system consists of:
        - **Soldier Wearable**: Monitors vitals (Heart rate, SpO2, core temp), detects blast shocks (>4.5g) or falls, and features an SOS switch.
        - **Tactical Relays**: Autonomous solar-buffered repeaters on mountain ridges that forward packets across terrain shadows.
        - **Base Gateway**: Receives packets, sounds local acoustic sirens, and feeds this command dashboard.
        
        *Notice: This is a software simulation-first proof of concept.*
        """
    },
    {
        "id": "metrics",
        "title": "2. Meaning of Telemetry Metrics & Symbols",
        "category": "Telemetry & Sensors",
        "summary": "Explanation of Heart Rate, SpO2, Body Temperature, Impact G-Force, and Battery.",
        "content": """
        Each deployed soldier node transmits these key physiological and kinematic metrics:
        
        - **Heart Rate (BPM)**: Beats per minute. Normal baseline: 60–100 BPM. Warning: >120 BPM. Emergency (Cardiac Anomaly): <45 or >160 BPM.
        - **Blood Oxygen Saturation (SpO2 %)**: Arterial oxygenation. Normal: 95–100%. Warning (Mild Hypoxia): 89–94%. Critical Emergency: <88%.
        - **Body Temperature (°C)**: Normal core temperature: 36.5–37.2°C. Hypothermia Alert: <35.0°C (Siachen cold stress). Heatstroke: >39.5°C.
        - **Impact Shock (g-force)**: Instantaneous 3-axis acceleration magnitude. Normal patrol: ~1.0g. Tactical sprint: up to 2.5g. **Blast Shock / Explosion Emergency: ≥4.5g**.
        - **Fall Event**: Flags freefall (<0.4g) followed by sudden impact and prolonged immobility (>10s stillness).
        - **Signal Strength (RSSI dBm)**: Received Signal Strength Indication. Above -80 dBm: Excellent. -80 to -100 dBm: Moderate. Below -110 dBm: Weak/attenuated.
        - **Hop Count**: The number of relay repeaters traversed to reach the command base.
        """
    },
    {
        "id": "status_reading",
        "title": "3. How to Read Personnel Status Cards",
        "category": "Personnel Monitoring",
        "summary": "Understanding SAFE (Green), WARNING (Amber), and EMERGENCY (Red) indicators.",
        "content": """
        Personnel are automatically classified into three tactical states:
        
        - **🟢 SAFE (Nominal)**: All physiological vitals and motion vectors are within normal limits. Telemetry is sent every 3000ms.
        - **🟡 WARNING (Caution)**: Non-critical anomalies detected, such as low battery (≤15%), elevated heart rate from exertion, or mild thermal drops. Telemetry is sent every 1500ms.
        - **🔴 EMERGENCY (Casualty)**: Critical trauma detected! Triggered by manual SOS push button, blast impact ≥4.5g, fall with immobility, or severe hypothermia (<35°C). Strobe flashers activate, and distress packets broadcast every 750ms.
        """
    },
    {
        "id": "sos_simulation",
        "title": "4. How to Trigger & Reset an Emergency Simulation",
        "category": "Simulations",
        "summary": "Step-by-step instructions for running safe demo trauma events and resetting.",
        "content": """
        To simulate an emergency without real hardware:
        
        1. Open the **Emergency Simulation** tab from the sidebar.
        2. Select the soldier you wish to test (e.g., **Delta-1 Sepoy Rajesh Kumar**).
        3. Click an incident button:
           - **🚨 Trigger SOS**: Simulates manual tactile emergency button press.
           - **💥 Blast Shock (>5g)**: Simulates concussive blast wave (5.6g) with subsequent immobility.
           - **🤸 Fall & Collapse**: Simulates a slip, freefall, and prolonged stillness.
           - **❄️ Hypothermia (<34°C)**: Simulates severe sub-zero thermal collapse.
        4. Observe the instant status transition and event log entry.
        5. To restore nominal conditions, click **🔄 Reset Simulation to Safe**.
        """
    },
    {
        "id": "relay_failover",
        "title": "5. Understanding Relay Nodes & Self-Healing Mesh",
        "category": "Network & Mesh",
        "summary": "How autonomous repeaters reroute telemetry when a mountain relay fails.",
        "content": """
        Because mountain ridges block direct line-of-sight RF, SURAKSHA-NET deploys autonomous solar repeaters:
        
        - **Relay-01 (Ridge-Repeater-Alpha)**: Primary elevated repeater node.
        - **Relay-02 (Ridge-Repeater-Bravo)**: Secondary alternate mesh node.
        
        **Dynamic Failover Demonstration**:
        1. Navigate to **Network & Relay Status** or click **Toggle Relay-01** in the sidebar.
        2. When Relay-01 is toggled to **OFFLINE**, the system's decentralized routing algorithm automatically hops packets through **Relay-02**.
        3. The active RF route updates from:
           `SOLDIER-01 ➔ RELAY-01 ➔ BASE` to `SOLDIER-01 ➔ RELAY-02 (Alternate) ➔ BASE`.
        """
    },
    {
        "id": "event_logs",
        "title": "6. Viewing & Exporting Emergency Logs",
        "category": "Logs & Reports",
        "summary": "How to inspect transmission records, filter duplicate drops, and download CSV reports.",
        "content": """
        Every transmission is logged in the **Event Logs** section:
        
        - **Message ID (msg_id)**: Unique transmission sequence code.
        - **Alert Type**: Reason for transmission (`PERIODIC_TELEMETRY`, `MANUAL_SOS`, `IMPACT_CRITICAL`, `ROUTE_FAILOVER`).
        - **Delivery Status**: `DELIVERED` (Direct or via relay), `DELIVERED_FAILOVER` (via backup mesh), or `DROPPED_DUPLICATE` (filtered to prevent RF congestion).
        - **Export**: Click the **📥 Export Incident Log (CSV)** button to save the mission record for post-action debriefing.
        """
    },
    {
        "id": "troubleshooting",
        "title": "7. Troubleshooting Common Issues",
        "category": "Troubleshooting",
        "summary": "Solutions for port conflicts, missing packages, and browser display issues.",
        "content": r"""
        - **Port 8501 Already in Use**: If another Streamlit instance is running, launch on another port:
          `.\.venv\Scripts\streamlit.exe run dashboard\app.py --server.port 8502`
        - **AI Assistant Shows 'Demo Assistant'**: This is normal when no Gemini API key is configured. To enable live generative AI, set `GEMINI_API_KEY` in your environment or Streamlit secrets.
        - **Map Not Displaying Pins**: Ensure your browser allows WebGL. The coordinates represent a simulated sector in Ladakh/Kargil.
        - **Tests Failing**: Run `.\.venv\Scripts\python.exe simulation\test_scenarios.py` to inspect failure logs.
        """
    },
    {
        "id": "windows_controls",
        "title": "8. How to Start and Stop on Windows",
        "category": "Operations",
        "summary": "Exact PowerShell commands to launch and terminate the dashboard.",
        "content": r"""
        **To Start the Application**:
        ```powershell
        cd c:\Users\DELL\OneDrive\Desktop\SURAKSHA-NET
        .\.venv\Scripts\streamlit.exe run dashboard\app.py
        ```
        
        **To Run Automated Tests**:
        ```powershell
        .\.venv\Scripts\python.exe simulation\test_scenarios.py
        ```
        
        **To Stop the Server**:
        In the running PowerShell window, press `Ctrl + C` and confirm termination.
        """
    }
]

TOUR_STEPS = [
    {
        "step": 1,
        "title": "Step 1: System Header & Real-time Status",
        "description": "The top banner displays the tactical header, current operational readiness, and any active critical casualty alerts. If an emergency occurs, a pulsing red banner alerts you immediately across every page."
    },
    {
        "step": 2,
        "title": "Step 2: Summary Metric Counters",
        "description": "Directly below the header are the 5 high-level tactical counters: Total Deployed Units, Safe Patrols, Warning State, Critical Emergencies, and Active Relay Nodes. These give commanders an instant overview of squad health."
    },
    {
        "step": 3,
        "title": "Step 3: Personnel Monitoring Tab",
        "description": "Switch to 'Personnel Monitoring' in the sidebar to inspect individual soldier vitals (Heart rate, SpO2, core temperature, acceleration impact force, and battery percentage)."
    },
    {
        "step": 4,
        "title": "Step 4: Interactive Emergency Simulations",
        "description": "In 'Emergency Simulation', you can safely test the triage engine by injecting simulated blast shocks (>5g), manual SOS calls, or hypothermia events, and observe the immediate state transitions."
    },
    {
        "step": 5,
        "title": "Step 5: Self-Healing Mesh Network",
        "description": "In 'Network & Relay Status', toggle Relay-01 offline to watch the system demonstrate dynamic rerouting through Relay-02 without dropped packets."
    },
    {
        "step": 6,
        "title": "Step 6: High-Altitude Tactical GIS Map",
        "description": "Under 'Map & Sector View', explore the 3D-emulated deployment grid showing soldier positions, relay towers, and tactical base headquarters."
    },
    {
        "step": 7,
        "title": "Step 7: Mission Event Audit Log",
        "description": "Check 'Event Logs' for a full timestamped chronological audit trail of all alerts, hop counts, and delivery paths, complete with one-click CSV export."
    },
    {
        "step": 8,
        "title": "Step 8: Ask SURAKSHA AI Assistant",
        "description": "Use the floating button at bottom-right or select 'AI Assistant' in the sidebar to ask questions in English or Tenglish. The AI explains readings, guides actions, and analyzes incidents!"
    }
]


def render_help_center():
    """Renders the comprehensive Help Center with searchable cards and Guided Tour."""
    st.subheader("📖 Help Assistant & User Knowledge Base")
    st.caption("Learn how to operate the SURAKSHA-NET dashboard, interpret telemetry, and run simulations.")

    # 1. Interactive "Guide Me" Walkthrough Feature
    with st.expander("🚀 Interactive 'Guide Me' Walkthrough (Step-by-Step Tour)", expanded=st.session_state.get("tour_active", False)):
        if "tour_step" not in st.session_state:
            st.session_state.tour_step = 0
            st.session_state.tour_active = False

        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            if not st.session_state.tour_active:
                st.write("New to the dashboard? Start an interactive step-by-step tour that explains every key section!")
                if st.button("▶️ Start Guided Tour", key="btn_start_tour"):
                    st.session_state.tour_active = True
                    st.session_state.tour_step = 0
                    st.rerun()
            else:
                curr_idx = st.session_state.tour_step
                step_data = TOUR_STEPS[curr_idx]

                st.markdown(f"""
                <div class="guide-box">
                    <span style="font-size: 11.5px; text-transform: uppercase; letter-spacing: 1px; color: #58a6ff; font-weight: 700;">
                        SURAKSHA-NET GUIDED TOUR ({curr_idx + 1} of {len(TOUR_STEPS)})
                    </span>
                    <h3 style="margin: 6px 0 10px 0; color: #ffffff;">{step_data['title']}</h3>
                    <p style="font-size: 14.5px; line-height: 1.6; color: #c9d1d9; margin: 0;">
                        {step_data['description']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Navigation Buttons: Back, Next, Exit
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1.5])
                with btn_col1:
                    if st.button("⬅️ Previous", disabled=(curr_idx == 0), key="btn_tour_prev"):
                        st.session_state.tour_step = max(0, curr_idx - 1)
                        st.rerun()
                with btn_col2:
                    if curr_idx < len(TOUR_STEPS) - 1:
                        if st.button("Next ➡️", key="btn_tour_next"):
                            st.session_state.tour_step = curr_idx + 1
                            st.rerun()
                    else:
                        if st.button("Finish 🎉", key="btn_tour_finish"):
                            st.session_state.tour_active = False
                            st.session_state.tour_step = 0
                            st.success("Tour complete! You're ready to use SURAKSHA-NET.")
                            st.rerun()
                with btn_col3:
                    if st.button("Exit Tour ✖️", key="btn_tour_exit"):
                        st.session_state.tour_active = False
                        st.session_state.tour_step = 0
                        st.rerun()

    st.markdown("---")

    # 2. Searchable Help Topic Cards
    search_query = st.text_input(
        "🔍 Search Help Topics (e.g., 'vitals', 'failover', 'SOS', 'battery', 'export', 'windows')",
        placeholder="Type a keyword to filter help cards..."
    ).strip().lower()

    # Filter topics
    if search_query:
        matched_topics = [
            t for t in HELP_TOPICS
            if search_query in t["title"].lower() or search_query in t["summary"].lower() or search_query in t["content"].lower()
        ]
        st.caption(f"Showing {len(matched_topics)} matching topics for '{html.escape(search_query)}':")
    else:
        matched_topics = HELP_TOPICS

    if not matched_topics:
        st.info(f"No help topics matched '{search_query}'. Try searching for 'vitals', 'SOS', 'failover', or 'logs'.")

    for topic in matched_topics:
        with st.expander(f"{topic['title']} — *{topic['category']}*", expanded=bool(search_query)):
            st.markdown(f"**{topic['summary']}**")
            st.markdown(topic['content'])

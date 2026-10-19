"""
SURAKSHA-NET Mesh Network & Tactical Personnel Simulator
Smart Soldier Protection, Survival & Rescue System

SIMULATION NOTICE:
This module simulates multi-node LoRa/RF mesh communications, dynamic rerouting,
node failover, and soldier physiological telemetry. It is a zero-cost software
proof of concept and does NOT represent measured RF propagation or hardware timing.
"""

import time
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import copy

from protocol import (
    SystemState,
    AlertType,
    Vitals,
    Kinematics,
    GPSCoordinates,
    NetworkMetadata,
    PowerStatus,
    TelemetryPacket,
    evaluate_emergency_state,
    THRESHOLDS,
)


class MeshSimulator:
    """Simulates soldier wearable nodes, tactical relays, and base station reception."""

    def __init__(self):
        self.message_counter = 1000
        self.event_counter = 100
        self.seen_messages: set = set()
        self.event_log: List[Dict[str, Any]] = []

        # Infrastructure state
        self.relay_status = {
            "RELAY-01": {"name": "Ridge-Repeater-Alpha (Primary)", "operational": True, "location": "Ridge Post 14"},
            "RELAY-02": {"name": "Ridge-Repeater-Bravo (Alternate)", "operational": True, "location": "Observation Post 3"},
        }

        # Baseline soldier profiles
        self.soldiers: Dict[str, Dict[str, Any]] = {
            "SOLDIER-01": {
                "id": "SOLDIER-01",
                "name": "Sepoy Rajesh Kumar",
                "callsign": "DELTA-LEAD",
                "unit": "3rd Battalion (High Altitude Patrol)",
                "status": SystemState.SAFE,
                "alert_type": AlertType.PERIODIC_TELEMETRY,
                "manual_sos": False,
                "vitals": Vitals(heart_rate_bpm=72, spo2_percent=98, body_temp_c=36.7),
                "kinematics": Kinematics(accel_x_g=0.05, accel_y_g=0.08, accel_z_g=0.99, impact_g=1.0, fall_detected=False, is_immobile=False),
                "gps": GPSCoordinates(latitude=35.4211, longitude=77.1095, altitude_m=5420.0),
                "power": PowerStatus(battery_pct=88, voltage_v=3.95, is_low_battery=False),
                "preferred_relay": "RELAY-01",
            },
            "SOLDIER-02": {
                "id": "SOLDIER-02",
                "name": "Lance Naik Amit Singh",
                "callsign": "DELTA-SCOUT",
                "unit": "3rd Battalion (Valley Reconnaissance)",
                "status": SystemState.SAFE,
                "alert_type": AlertType.PERIODIC_TELEMETRY,
                "manual_sos": False,
                "vitals": Vitals(heart_rate_bpm=84, spo2_percent=97, body_temp_c=36.9),
                "kinematics": Kinematics(accel_x_g=0.12, accel_y_g=0.15, accel_z_g=0.98, impact_g=1.1, fall_detected=False, is_immobile=False),
                "gps": GPSCoordinates(latitude=34.4285, longitude=75.7615, altitude_m=3280.0),
                "power": PowerStatus(battery_pct=92, voltage_v=4.05, is_low_battery=False),
                "preferred_relay": "RELAY-01",
            },
            "SOLDIER-03": {
                "id": "SOLDIER-03",
                "name": "Havildar Vikram Thapa",
                "callsign": "DELTA-REAR",
                "unit": "3rd Battalion (Support Element)",
                "status": SystemState.SAFE,
                "alert_type": AlertType.PERIODIC_TELEMETRY,
                "manual_sos": False,
                "vitals": Vitals(heart_rate_bpm=68, spo2_percent=99, body_temp_c=36.6),
                "kinematics": Kinematics(accel_x_g=0.02, accel_y_g=0.04, accel_z_g=1.01, impact_g=0.98, fall_detected=False, is_immobile=False),
                "gps": GPSCoordinates(latitude=34.5539, longitude=76.1349, altitude_m=4120.0),
                "power": PowerStatus(battery_pct=76, voltage_v=3.82, is_low_battery=False),
                "preferred_relay": "RELAY-01",
            },
        }

        # Generate initial system online log
        self._log_event(
            msg_id="SYS-BOOT-0001",
            origin_id="SYSTEM",
            personnel="Command Base Gateway",
            alert_type="SYSTEM_BOOT",
            status=SystemState.SAFE,
            route=["BASE_GATEWAY"],
            delivery="SUCCESS",
            details="SURAKSHA-NET Tactical Rescue Command gateway online. All simulated nodes initialized.",
            location="Command HQ (34.2000°N, 76.0000°E)",
            recommended_step="All systems nominal. Ready for mission telemetry ingestion.",
        )

    def _next_msg_id(self) -> str:
        self.message_counter += 1
        return f"SN-{datetime.now(timezone.utc).strftime('%H%M%S')}-{self.message_counter:04d}"

    def _next_event_id(self) -> str:
        self.event_counter += 1
        return f"EVT-{self.event_counter:04d}"

    def _log_event(
        self,
        msg_id: str,
        origin_id: str,
        personnel: str,
        alert_type: str,
        status: SystemState,
        route: List[str],
        delivery: str,
        details: str,
        location: Optional[str] = None,
        recommended_step: Optional[str] = None,
    ):
        event_id = self._next_event_id()
        status_str = status.value if isinstance(status, SystemState) else str(status)
        alert_str = alert_type.value if isinstance(alert_type, AlertType) else str(alert_type)

        # Compute severity
        if status_str == "EMERGENCY":
            severity = "CRITICAL"
        elif status_str == "WARNING":
            severity = "WARNING"
        else:
            severity = "NORMAL"

        # Auto-compute location if missing
        if not location:
            if origin_id in self.soldiers:
                g = self.soldiers[origin_id]["gps"]
                location = f"{g.latitude:.4f}°N, {g.longitude:.4f}°E ({g.altitude_m:.0f}m)"
            else:
                location = "Tactical Base HQ (Ladakh Sector)"

        # Auto-compute recommended step if missing
        if not recommended_step:
            if severity == "CRITICAL":
                recommended_step = f"🚨 Immediate casualty dispatch to {location}. Alert medical trauma team."
            elif severity == "WARNING":
                recommended_step = "⚠️ Monitor vitals trend and signal squad to check battery/thermal gear."
            elif alert_str == "ROUTE_FAILOVER":
                recommended_step = "🌐 Dispatch comms technician to inspect offline relay node."
            else:
                recommended_step = "✅ Maintain routine periodic patrol telemetry monitoring."

        entry = {
            "event_id": event_id,
            "sim_badge": "SIMULATED",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "msg_id": msg_id,
            "origin_id": origin_id,
            "personnel": personnel,
            "severity": severity,
            "status": status_str,
            "alert_type": alert_str,
            "location": location,
            "recommended_step": recommended_step,
            "route": " -> ".join(route),
            "delivery": delivery,
            "details": details,
        }
        self.event_log.insert(0, entry)
        if len(self.event_log) > 120:
            self.event_log.pop()

    def determine_route(self, soldier_id: str) -> Tuple[List[str], int, int, bool, str]:
        """
        Calculates network mesh route from soldier wearable to rescue base station.
        Returns: (route_path, hop_count, rssi_dbm, backup_route_active, delivery_status)
        """
        primary = "RELAY-01"
        backup = "RELAY-02"

        if self.relay_status[primary]["operational"]:
            # Route: Wearable -> Relay-01 -> Base Station
            route = [soldier_id, primary, "BASE-COMMAND-01"]
            return route, 2, random.randint(-78, -70), False, "DELIVERED"
        elif self.relay_status[backup]["operational"]:
            # Rerouted: Wearable -> Relay-02 (Alternate) -> Base Station
            route = [soldier_id, backup, "BASE-COMMAND-01"]
            return route, 2, random.randint(-92, -84), True, "DELIVERED_FAILOVER"
        else:
            # Both relays down: Direct communication attempt (simulated deep gorge attenuation)
            route = [soldier_id, "BASE-COMMAND-01 (DIRECT)"]
            success = random.random() > 0.40  # 40% packet drop without relay
            delivery = "DELIVERED_DIRECT" if success else "FAILED_OUT_OF_RANGE"
            return route, 1, random.randint(-118, -108), True, delivery

    def generate_packet(self, soldier_id: str, duplicate: bool = False) -> TelemetryPacket:
        """Generates and routes a telemetry packet for the specified soldier."""
        soldier = self.soldiers[soldier_id]

        # Evaluate state machine
        state, alert_type = evaluate_emergency_state(
            manual_sos=soldier["manual_sos"],
            vitals=soldier["vitals"],
            kinematics=soldier["kinematics"],
            power=soldier["power"],
            current_state=soldier["status"],
        )
        soldier["status"] = state
        soldier["alert_type"] = alert_type

        # Routing calculation
        route, hops, rssi, backup_active, delivery = self.determine_route(soldier_id)

        msg_id = self._next_msg_id()
        if duplicate:
            msg_id = f"DUP-{msg_id}"

        net = NetworkMetadata(
            rssi_dbm=rssi,
            snr_db=round(random.uniform(6.0, 10.5), 1),
            hop_count=hops,
            route=route,
            backup_route_active=backup_active,
        )

        packet = TelemetryPacket(
            msg_id=msg_id,
            timestamp=int(datetime.now(timezone.utc).timestamp()),
            node_id=route[-1],
            origin_id=soldier_id,
            personnel_name=soldier["name"],
            callsign=soldier["callsign"],
            status=state,
            alert_type=alert_type,
            vitals=copy.deepcopy(soldier["vitals"]),
            kinematics=copy.deepcopy(soldier["kinematics"]),
            gps=copy.deepcopy(soldier["gps"]),
            network=net,
            power=copy.deepcopy(soldier["power"]),
        )
        packet.seal()

        # Deduplication & Logging logic
        g = soldier["gps"]
        loc_str = f"{g.latitude:.4f}°N, {g.longitude:.4f}°E (Alt {g.altitude_m:.0f}m)"

        if packet.msg_id in self.seen_messages:
            self._log_event(
                msg_id=packet.msg_id,
                origin_id=soldier_id,
                personnel=soldier["name"],
                alert_type="DUPLICATE_PACKET",
                status=state,
                route=route,
                delivery="DROPPED_DUPLICATE",
                details="Mesh repeater dropped duplicate message frame to conserve RF channel capacity.",
                location=loc_str,
                recommended_step="Packet dropped by in-memory deduplication cache. No action needed.",
            )
        else:
            self.seen_messages.add(packet.msg_id)
            if delivery.startswith("DELIVERED"):
                detail_msg = f"Alert {alert_type.value} received via route [{' -> '.join(route)}]."
                if backup_active:
                    detail_msg += " (Alternate relay mesh failover active)."
                self._log_event(
                    msg_id=packet.msg_id,
                    origin_id=soldier_id,
                    personnel=soldier["name"],
                    alert_type=alert_type.value,
                    status=state,
                    route=route,
                    delivery=delivery,
                    details=detail_msg,
                    location=loc_str,
                )
            else:
                self._log_event(
                    msg_id=packet.msg_id,
                    origin_id=soldier_id,
                    personnel=soldier["name"],
                    alert_type=alert_type.value,
                    status=state,
                    route=route,
                    delivery="FAILED_NO_ROUTE",
                    details="Direct link attempted but packet dropped due to terrain obstruction. Relays offline.",
                    location=loc_str,
                    recommended_step="Critical RF link failure. Re-position mobile drone repeater.",
                )

        return packet

    def trigger_sos(self, soldier_id: str) -> TelemetryPacket:
        if soldier_id in self.soldiers:
            self.soldiers[soldier_id]["manual_sos"] = True
            return self.generate_packet(soldier_id)
        raise ValueError(f"Soldier {soldier_id} not found")

    def trigger_impact(self, soldier_id: str, impact_g: float = 5.2) -> TelemetryPacket:
        if soldier_id in self.soldiers:
            self.soldiers[soldier_id]["kinematics"].impact_g = impact_g
            self.soldiers[soldier_id]["kinematics"].fall_detected = True
            self.soldiers[soldier_id]["kinematics"].is_immobile = True
            # Elevate heart rate due to physiological shock
            self.soldiers[soldier_id]["vitals"].heart_rate_bpm = 138
            return self.generate_packet(soldier_id)
        raise ValueError(f"Soldier {soldier_id} not found")

    def trigger_temp_warning(self, soldier_id: str, temp_c: float = 33.8) -> TelemetryPacket:
        if soldier_id in self.soldiers:
            self.soldiers[soldier_id]["vitals"].body_temp_c = temp_c
            return self.generate_packet(soldier_id)
        raise ValueError(f"Soldier {soldier_id} not found")

    def trigger_fall(self, soldier_id: str, immobile: bool = True) -> TelemetryPacket:
        if soldier_id in self.soldiers:
            self.soldiers[soldier_id]["kinematics"].fall_detected = True
            self.soldiers[soldier_id]["kinematics"].is_immobile = immobile
            self.soldiers[soldier_id]["kinematics"].impact_g = 3.6
            return self.generate_packet(soldier_id)
        raise ValueError(f"Soldier {soldier_id} not found")

    def trigger_cardiac_warning(self, soldier_id: str, hr: int = 168, spo2: int = 86) -> TelemetryPacket:
        if soldier_id in self.soldiers:
            self.soldiers[soldier_id]["vitals"].heart_rate_bpm = hr
            self.soldiers[soldier_id]["vitals"].spo2_percent = spo2
            return self.generate_packet(soldier_id)
        raise ValueError(f"Soldier {soldier_id} not found")

    def toggle_relay_failure(self, relay_id: str = "RELAY-01") -> bool:
        if relay_id in self.relay_status:
            curr = self.relay_status[relay_id]["operational"]
            self.relay_status[relay_id]["operational"] = not curr
            new_state = self.relay_status[relay_id]["operational"]
            state_str = "RESTORED ONLINE" if new_state else "SIMULATED FAILURE / OFFLINE"
            rec_step = "Relay operational. Primary mesh path active." if new_state else "Primary relay offline. Directing mesh traffic over secondary repeater."
            self._log_event(
                msg_id=self._next_msg_id(),
                origin_id="NETWORK_MONITOR",
                personnel="Mesh Coordinator",
                alert_type="ROUTE_FAILOVER",
                status=SystemState.WARNING if not new_state else SystemState.SAFE,
                route=[relay_id, "BASE-COMMAND-01"],
                delivery="STATUS_CHANGE",
                details=f"Repeater node {relay_id} ({self.relay_status[relay_id]['name']}) transitioned to: {state_str}",
                location=self.relay_status[relay_id]["location"],
                recommended_step=rec_step,
            )
            return new_state
        return False

    def reset_soldier(self, soldier_id: str) -> TelemetryPacket:
        if soldier_id in self.soldiers:
            self.soldiers[soldier_id]["manual_sos"] = False
            self.soldiers[soldier_id]["vitals"] = Vitals(heart_rate_bpm=72, spo2_percent=98, body_temp_c=36.7)
            self.soldiers[soldier_id]["kinematics"] = Kinematics(accel_x_g=0.04, accel_y_g=0.06, accel_z_g=0.99, impact_g=1.0, fall_detected=False, is_immobile=False)
            self.soldiers[soldier_id]["power"].battery_pct = max(70, self.soldiers[soldier_id]["power"].battery_pct)
            self.soldiers[soldier_id]["status"] = SystemState.SAFE
            self.soldiers[soldier_id]["alert_type"] = AlertType.SYSTEM_RESET
            packet = self.generate_packet(soldier_id)
            return packet
        raise ValueError(f"Soldier {soldier_id} not found")

    def run_safe_scenario(self):
        """Restores all soldiers and relays to nominal baseline patrolling status."""
        for s_id in self.soldiers:
            self.reset_soldier(s_id)
        self.relay_status["RELAY-01"]["operational"] = True
        self.relay_status["RELAY-02"]["operational"] = True
        self._log_event(
            msg_id=self._next_msg_id(),
            origin_id="SCENARIO_RUNNER",
            personnel="Command Controller",
            alert_type="SCENARIO_SAFE",
            status=SystemState.SAFE,
            route=["ALL_NODES", "BASE-COMMAND-01"],
            delivery="SUCCESS",
            details="Safe Demo Scenario Applied: All squad personnel and relay repeaters restored to nominal baseline.",
            location="Ladakh High-Altitude Patrol Sector",
            recommended_step="All units operating normally. Continue standard mission schedule.",
        )

    def reset_all(self):
        """Clears all emergency latches and restores full squad to safe state."""
        self.run_safe_scenario()

    def step_simulation(self):
        """Simulates physiological sensor jitter and subtle GPS drift."""
        for s_id, s in self.soldiers.items():
            if s["status"] == SystemState.SAFE:
                # Normal fluctuations
                s["vitals"].heart_rate_bpm = max(60, min(100, s["vitals"].heart_rate_bpm + random.choice([-1, 0, 1])))
                s["vitals"].body_temp_c = round(max(36.2, min(37.2, s["vitals"].body_temp_c + random.uniform(-0.03, 0.03))), 1)
                # GPS micro-drift
                s["gps"].latitude = round(s["gps"].latitude + random.uniform(-0.00003, 0.00003), 5)
                s["gps"].longitude = round(s["gps"].longitude + random.uniform(-0.00003, 0.00003), 5)

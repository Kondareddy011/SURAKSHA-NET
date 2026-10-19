"""
SURAKSHA-NET Automated Test Suite
Smart Soldier Protection, Survival & Rescue System

Tests:
1. Emergency State Transitions
2. Message Formatting & Checksum Verification
3. Invalid / Corrupted Telemetry Rejection
4. Relay Failure & Alternate Routing Failover
5. Duplicate Message Filtering
6. Scenario JSON Schema Conformance
"""

import sys
import os
import json
import unittest

# Add dashboard directory to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard")))

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
from simulator import MeshSimulator


class TestEmergencyStateTransitions(unittest.TestCase):
    """Verifies that unvalidated engineering thresholds trigger the appropriate states."""

    def setUp(self):
        self.nominal_vitals = Vitals(heart_rate_bpm=75, spo2_percent=98, body_temp_c=36.8)
        self.nominal_kinematics = Kinematics(impact_g=1.0, fall_detected=False, is_immobile=False)
        self.nominal_power = PowerStatus(battery_pct=85, voltage_v=3.95)

    def test_nominal_state_is_safe(self):
        state, alert = evaluate_emergency_state(
            manual_sos=False,
            vitals=self.nominal_vitals,
            kinematics=self.nominal_kinematics,
            power=self.nominal_power,
        )
        self.assertEqual(state, SystemState.SAFE)
        self.assertEqual(alert, AlertType.PERIODIC_TELEMETRY)

    def test_manual_sos_overrides_all(self):
        state, alert = evaluate_emergency_state(
            manual_sos=True,
            vitals=self.nominal_vitals,
            kinematics=self.nominal_kinematics,
            power=self.nominal_power,
        )
        self.assertEqual(state, SystemState.EMERGENCY)
        self.assertEqual(alert, AlertType.MANUAL_SOS)

    def test_blast_impact_triggers_emergency(self):
        impact_kinematics = Kinematics(impact_g=5.5, fall_detected=True, is_immobile=True)
        state, alert = evaluate_emergency_state(
            manual_sos=False,
            vitals=self.nominal_vitals,
            kinematics=impact_kinematics,
            power=self.nominal_power,
        )
        self.assertEqual(state, SystemState.EMERGENCY)
        self.assertEqual(alert, AlertType.IMPACT_CRITICAL)

    def test_fall_with_immobility_triggers_emergency(self):
        fall_kinematics = Kinematics(impact_g=2.8, fall_detected=True, is_immobile=True)
        state, alert = evaluate_emergency_state(
            manual_sos=False,
            vitals=self.nominal_vitals,
            kinematics=fall_kinematics,
            power=self.nominal_power,
        )
        self.assertEqual(state, SystemState.EMERGENCY)
        self.assertEqual(alert, AlertType.FALL_DETECTED)

    def test_hypothermia_triggers_emergency(self):
        cold_vitals = Vitals(heart_rate_bpm=65, spo2_percent=96, body_temp_c=34.2)
        state, alert = evaluate_emergency_state(
            manual_sos=False,
            vitals=cold_vitals,
            kinematics=self.nominal_kinematics,
            power=self.nominal_power,
        )
        self.assertEqual(state, SystemState.EMERGENCY)
        self.assertEqual(alert, AlertType.HYPOTHERMIA)

    def test_heatstroke_triggers_emergency(self):
        hot_vitals = Vitals(heart_rate_bpm=135, spo2_percent=95, body_temp_c=40.2)
        state, alert = evaluate_emergency_state(
            manual_sos=False,
            vitals=hot_vitals,
            kinematics=self.nominal_kinematics,
            power=self.nominal_power,
        )
        self.assertEqual(state, SystemState.EMERGENCY)
        self.assertEqual(alert, AlertType.HEAT_STROKE)

    def test_low_battery_triggers_warning(self):
        low_pwr = PowerStatus(battery_pct=15, voltage_v=3.45)
        state, alert = evaluate_emergency_state(
            manual_sos=False,
            vitals=self.nominal_vitals,
            kinematics=self.nominal_kinematics,
            power=low_pwr,
        )
        self.assertEqual(state, SystemState.WARNING)
        self.assertEqual(alert, AlertType.PERIODIC_TELEMETRY)


class TestProtocolSerializationAndChecksum(unittest.TestCase):
    """Verifies JSON protocol serialization, round-trip deserialization, and CRC checksums."""

    def setUp(self):
        self.packet = TelemetryPacket(
            msg_id="TEST-0001",
            timestamp=1729074000,
            node_id="BASE-COMMAND-01",
            origin_id="SOLDIER-01",
            personnel_name="Sepoy Rajesh Kumar",
            callsign="DELTA-LEAD",
            status=SystemState.SAFE,
            alert_type=AlertType.PERIODIC_TELEMETRY,
            vitals=Vitals(heart_rate_bpm=74, spo2_percent=98, body_temp_c=36.7),
            kinematics=Kinematics(impact_g=1.0),
            gps=GPSCoordinates(latitude=35.4211, longitude=77.1095, altitude_m=5420.0),
            network=NetworkMetadata(rssi_dbm=-75, hop_count=2, route=["SOLDIER-01", "RELAY-01", "BASE-01"]),
            power=PowerStatus(battery_pct=88, voltage_v=3.95),
        )
        self.packet.seal()

    def test_checksum_valid(self):
        self.assertTrue(self.packet.verify_checksum())

    def test_checksum_fails_on_tampering(self):
        tampered = TelemetryPacket.from_dict(self.packet.to_dict())
        tampered.vitals.heart_rate_bpm = 180  # Tampered without recalculating checksum
        self.assertFalse(tampered.verify_checksum())

    def test_json_roundtrip(self):
        json_str = self.packet.to_json()
        restored = TelemetryPacket.from_json(json_str)
        self.assertEqual(restored.msg_id, self.packet.msg_id)
        self.assertEqual(restored.vitals.heart_rate_bpm, self.packet.vitals.heart_rate_bpm)
        self.assertEqual(restored.status, self.packet.status)
        self.assertTrue(restored.verify_checksum())


class TestInvalidDataHandling(unittest.TestCase):
    """Verifies that out-of-bounds or physically impossible sensor values are rejected."""

    def test_invalid_heart_rate_rejected(self):
        v = Vitals(heart_rate_bpm=350)
        ok, err = v.validate()
        self.assertFalse(ok)
        self.assertIn("Heart rate out of physiological range", err)

    def test_invalid_spo2_rejected(self):
        v = Vitals(spo2_percent=110)
        ok, err = v.validate()
        self.assertFalse(ok)
        self.assertIn("SpO2 out of physiological range", err)

    def test_invalid_temperature_rejected(self):
        v = Vitals(body_temp_c=65.0)
        ok, err = v.validate()
        self.assertFalse(ok)
        self.assertIn("Body temperature out of range", err)

    def test_invalid_gps_rejected(self):
        gps = GPSCoordinates(latitude=120.0, longitude=77.0)
        ok, err = gps.validate()
        self.assertFalse(ok)
        self.assertIn("Latitude out of bounds", err)

    def test_negative_battery_rejected(self):
        pwr = PowerStatus(battery_pct=-10)
        ok, err = pwr.validate()
        self.assertFalse(ok)
        self.assertIn("Battery percentage out of range", err)


class TestMeshSimulatorAndFailover(unittest.TestCase):
    """Verifies routing, failover when relay is disabled, and duplicate suppression."""

    def setUp(self):
        self.sim = MeshSimulator()

    def test_primary_route_active(self):
        route, hops, rssi, backup, delivery = self.sim.determine_route("SOLDIER-01")
        self.assertEqual(route, ["SOLDIER-01", "RELAY-01", "BASE-COMMAND-01"])
        self.assertFalse(backup)
        self.assertEqual(delivery, "DELIVERED")

    def test_relay_failover_to_backup(self):
        # Disable RELAY-01
        self.sim.toggle_relay_failure("RELAY-01")
        self.assertFalse(self.sim.relay_status["RELAY-01"]["operational"])

        # Check route now uses RELAY-02
        route, hops, rssi, backup, delivery = self.sim.determine_route("SOLDIER-01")
        self.assertEqual(route, ["SOLDIER-01", "RELAY-02", "BASE-COMMAND-01"])
        self.assertTrue(backup)
        self.assertEqual(delivery, "DELIVERED_FAILOVER")

    def test_trigger_sos_sets_emergency(self):
        packet = self.sim.trigger_sos("SOLDIER-01")
        self.assertEqual(packet.status, SystemState.EMERGENCY)
        self.assertEqual(packet.alert_type, AlertType.MANUAL_SOS)

    def test_trigger_impact_sets_emergency(self):
        packet = self.sim.trigger_impact("SOLDIER-02", impact_g=6.2)
        self.assertEqual(packet.status, SystemState.EMERGENCY)
        self.assertEqual(packet.alert_type, AlertType.IMPACT_CRITICAL)

    def test_reset_soldier_restores_safe_state(self):
        self.sim.trigger_sos("SOLDIER-01")
        packet = self.sim.reset_soldier("SOLDIER-01")
        self.assertEqual(packet.status, SystemState.SAFE)

    def test_event_log_records_events(self):
        self.sim.trigger_sos("SOLDIER-03")
        self.assertGreater(len(self.sim.event_log), 0)
        self.assertEqual(self.sim.event_log[0]["origin_id"], "SOLDIER-03")


class TestScenarioJSONFiles(unittest.TestCase):
    """Verifies that all scenario JSON files parse and contain required structure."""

    def test_scenarios_exist_and_valid(self):
        scenario_dir = os.path.dirname(__file__)
        files = [
            "scenario_normal.json",
            "scenario_warning.json",
            "scenario_emergency.json",
            "scenario_relay_failure.json",
        ]
        for f in files:
            path = os.path.join(scenario_dir, f)
            self.assertTrue(os.path.exists(path), f"File {f} does not exist")
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                self.assertIn("scenario_name", data)
                self.assertIn("personnel", data)
                self.assertEqual(len(data["personnel"]), 3)
                for p in data["personnel"]:
                    self.assertIn("msg_id", p)
                    self.assertIn("vitals", p)
                    self.assertIn("status", p)


class TestAIAssistant(unittest.TestCase):
    """Verifies SURAKSHA AI Assistant fallback, Tenglish support, and context awareness."""

    def setUp(self):
        from ai_assistant import SurakshaAIAssistant
        self.ai = SurakshaAIAssistant(force_local=True)
        self.sim = MeshSimulator()

    def test_local_demo_badge_returned(self):
        reply, badge = self.ai.generate_response("Explain the dashboard.", sim=self.sim)
        self.assertIn("Rule-Based", badge)
        self.assertIn("SURAKSHA-NET", reply)

    def test_personnel_status_query(self):
        reply, badge = self.ai.generate_response("Show active personnel status.", sim=self.sim)
        self.assertIn("Personnel", reply)
        self.assertIn("Delta-1", reply)

    def test_tenglish_query_recognition(self):
        reply, badge = self.ai.generate_response("Soldier status cheppu", sim=self.sim)
        self.assertIn("Tenglish", reply)
        self.assertIn("Rajesh Kumar", reply)

    def test_sos_explanation_query(self):
        reply, badge = self.ai.generate_response("How does the SOS system work?", sim=self.sim)
        self.assertIn("SOS", reply)
        self.assertIn("MPU-6050", reply)

    def test_context_awareness_includes_stats(self):
        context = self.ai.build_telemetry_context(self.sim)
        self.assertIn("CURRENT SIMULATED SYSTEM STATE", context)
        self.assertIn("SOLDIER-01", context)


class TestHelpCenter(unittest.TestCase):
    """Verifies knowledge base topic coverage and guided tour step count."""

    def test_topics_complete(self):
        from help_center import HELP_TOPICS, TOUR_STEPS
        topic_ids = [t["id"] for t in HELP_TOPICS]
        self.assertIn("overview", topic_ids)
        self.assertIn("metrics", topic_ids)
        self.assertIn("status_reading", topic_ids)
        self.assertIn("sos_simulation", topic_ids)
        self.assertIn("relay_failover", topic_ids)
        self.assertIn("event_logs", topic_ids)
        self.assertIn("troubleshooting", topic_ids)
        self.assertIn("windows_controls", topic_ids)
        self.assertGreaterEqual(len(TOUR_STEPS), 6)


if __name__ == "__main__":
    unittest.main()

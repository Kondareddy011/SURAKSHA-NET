"""
SURAKSHA-NET Protocol Specification & Data Models
Smart Soldier Protection, Survival & Rescue System

SIMULATION NOTICE:
This module defines the JSON telemetry and emergency message protocol for the
SURAKSHA-NET simulation proof-of-concept. All thresholds are engineering estimates
and have NOT been clinically or ballistically validated in live military trials.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import json
import zlib


class SystemState(str, Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    EMERGENCY = "EMERGENCY"


class AlertType(str, Enum):
    PERIODIC_TELEMETRY = "PERIODIC_TELEMETRY"
    MANUAL_SOS = "MANUAL_SOS"
    IMPACT_CRITICAL = "IMPACT_CRITICAL"
    FALL_DETECTED = "FALL_DETECTED"
    HYPOTHERMIA = "HYPOTHERMIA"
    HEAT_STROKE = "HEAT_STROKE"
    CARDIAC_ANOMALY = "CARDIAC_ANOMALY"
    LOW_BATTERY = "LOW_BATTERY"
    ROUTE_FAILOVER = "ROUTE_FAILOVER"
    SYSTEM_RESET = "SYSTEM_RESET"


class NodeRole(str, Enum):
    WEARABLE = "WEARABLE"
    RELAY = "RELAY"
    BASE_STATION = "BASE_STATION"


# Engineering Thresholds (UNVALIDATED - Proof of Concept Only)
THRESHOLDS = {
    "HEART_RATE_LOW_BPM": 45,
    "HEART_RATE_HIGH_BPM": 160,
    "SPO2_MIN_PERCENT": 88,
    "TEMP_HYPOTHERMIA_C": 35.0,
    "TEMP_HEATSTROKE_C": 39.5,
    "IMPACT_THRESHOLD_G": 4.5,
    "FALL_FREEFALL_G": 0.5,
    "FALL_IMPACT_G": 3.0,
    "BATTERY_LOW_PERCENT": 20,
    "BATTERY_CRITICAL_PERCENT": 10,
}


@dataclass
class Vitals:
    heart_rate_bpm: int = 75
    spo2_percent: int = 98
    body_temp_c: float = 36.8
    is_simulated: bool = True

    def validate(self) -> Tuple[bool, Optional[str]]:
        if not (30 <= self.heart_rate_bpm <= 250):
            return False, f"Heart rate out of physiological range: {self.heart_rate_bpm}"
        if not (50 <= self.spo2_percent <= 100):
            return False, f"SpO2 out of physiological range: {self.spo2_percent}"
        if not (20.0 <= self.body_temp_c <= 45.0):
            return False, f"Body temperature out of range: {self.body_temp_c}"
        return True, None


@dataclass
class Kinematics:
    accel_x_g: float = 0.0
    accel_y_g: float = 0.0
    accel_z_g: float = 1.0
    impact_g: float = 1.0
    fall_detected: bool = False
    is_immobile: bool = False

    def validate(self) -> Tuple[bool, Optional[str]]:
        if abs(self.impact_g) > 50.0:
            return False, f"Impact value unrealistic: {self.impact_g}"
        return True, None


@dataclass
class GPSCoordinates:
    latitude: float = 34.1526
    longitude: float = 77.5771
    altitude_m: float = 3500.0
    fix_quality: str = "3D_FIX_SIMULATED"

    def validate(self) -> Tuple[bool, Optional[str]]:
        if not (-90.0 <= self.latitude <= 90.0):
            return False, f"Latitude out of bounds: {self.latitude}"
        if not (-180.0 <= self.longitude <= 180.0):
            return False, f"Longitude out of bounds: {self.longitude}"
        return True, None


@dataclass
class NetworkMetadata:
    rssi_dbm: int = -75
    snr_db: float = 8.0
    hop_count: int = 0
    route: List[str] = field(default_factory=lambda: ["WEARABLE-01"])
    backup_route_active: bool = False


@dataclass
class PowerStatus:
    battery_pct: int = 100
    voltage_v: float = 4.10
    is_low_battery: bool = False

    def validate(self) -> Tuple[bool, Optional[str]]:
        if not (0 <= self.battery_pct <= 100):
            return False, f"Battery percentage out of range: {self.battery_pct}"
        if not (2.5 <= self.voltage_v <= 4.5):
            return False, f"Battery voltage out of range: {self.voltage_v}"
        return True, None


@dataclass
class TelemetryPacket:
    msg_id: str
    timestamp: int
    node_id: str
    origin_id: str
    personnel_name: str
    callsign: str
    status: SystemState
    alert_type: AlertType
    vitals: Vitals
    kinematics: Kinematics
    gps: GPSCoordinates
    network: NetworkMetadata
    power: PowerStatus
    checksum: str = ""

    def calculate_checksum(self) -> str:
        """Computes CRC-32 hex checksum of payload ignoring current checksum field."""
        data_to_hash = f"{self.msg_id}|{self.timestamp}|{self.origin_id}|{self.status}|{self.alert_type}|{self.vitals.heart_rate_bpm}|{self.vitals.spo2_percent}|{self.vitals.body_temp_c:.1f}|{self.kinematics.impact_g:.2f}|{self.gps.latitude:.4f}|{self.gps.longitude:.4f}|{self.power.battery_pct}"
        crc = zlib.crc32(data_to_hash.encode("utf-8"))
        return f"{crc:08X}"

    def seal(self) -> "TelemetryPacket":
        self.checksum = self.calculate_checksum()
        return self

    def verify_checksum(self) -> bool:
        if not self.checksum:
            return False
        return self.checksum == self.calculate_checksum()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["alert_type"] = self.alert_type.value
        return d

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryPacket":
        return cls(
            msg_id=data.get("msg_id", "UNKNOWN"),
            timestamp=data.get("timestamp", int(datetime.now(timezone.utc).timestamp())),
            node_id=data.get("node_id", "UNKNOWN"),
            origin_id=data.get("origin_id", "UNKNOWN"),
            personnel_name=data.get("personnel_name", "Unknown Soldier"),
            callsign=data.get("callsign", "N/A"),
            status=SystemState(data.get("status", SystemState.SAFE.value)),
            alert_type=AlertType(data.get("alert_type", AlertType.PERIODIC_TELEMETRY.value)),
            vitals=Vitals(**data.get("vitals", {})),
            kinematics=Kinematics(**data.get("kinematics", {})),
            gps=GPSCoordinates(**data.get("gps", {})),
            network=NetworkMetadata(**data.get("network", {})),
            power=PowerStatus(**data.get("power", {})),
            checksum=data.get("checksum", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "TelemetryPacket":
        return cls.from_dict(json.loads(json_str))

    def validate(self) -> Tuple[bool, List[str]]:
        """Performs full schema and physiological validation."""
        errors: List[str] = []
        if not self.msg_id:
            errors.append("Missing msg_id")
        if not self.origin_id:
            errors.append("Missing origin_id")

        ok, err = self.vitals.validate()
        if not ok:
            errors.append(f"Vitals error: {err}")

        ok, err = self.kinematics.validate()
        if not ok:
            errors.append(f"Kinematics error: {err}")

        ok, err = self.gps.validate()
        if not ok:
            errors.append(f"GPS error: {err}")

        ok, err = self.power.validate()
        if not ok:
            errors.append(f"Power error: {err}")

        if not self.verify_checksum():
            errors.append("Checksum verification failed")

        return len(errors) == 0, errors


def evaluate_emergency_state(
    manual_sos: bool,
    vitals: Vitals,
    kinematics: Kinematics,
    power: PowerStatus,
    current_state: SystemState = SystemState.SAFE,
) -> Tuple[SystemState, AlertType]:
    """
    Evaluates telemetry against unvalidated engineering thresholds to compute
    the appropriate system emergency level.
    """
    # 1. Manual SOS is always highest priority EMERGENCY
    if manual_sos:
        return SystemState.EMERGENCY, AlertType.MANUAL_SOS

    # 2. Critical Impact (Blast/Ballistic/Vehicle crash)
    if kinematics.impact_g >= THRESHOLDS["IMPACT_THRESHOLD_G"]:
        return SystemState.EMERGENCY, AlertType.IMPACT_CRITICAL

    # 3. Fall Detected with Immobility
    if kinematics.fall_detected and kinematics.is_immobile:
        return SystemState.EMERGENCY, AlertType.FALL_DETECTED

    # 4. Severe Physiological Distress (Emergency)
    if vitals.body_temp_c < THRESHOLDS["TEMP_HYPOTHERMIA_C"]:
        return SystemState.EMERGENCY, AlertType.HYPOTHERMIA

    if vitals.body_temp_c > THRESHOLDS["TEMP_HEATSTROKE_C"]:
        return SystemState.EMERGENCY, AlertType.HEAT_STROKE

    if (
        vitals.heart_rate_bpm < THRESHOLDS["HEART_RATE_LOW_BPM"]
        or vitals.heart_rate_bpm > THRESHOLDS["HEART_RATE_HIGH_BPM"]
        or vitals.spo2_percent < THRESHOLDS["SPO2_MIN_PERCENT"]
    ):
        return SystemState.EMERGENCY, AlertType.CARDIAC_ANOMALY

    # 5. Warning Conditions (Elevated vitals, fall without immobility, low battery)
    if kinematics.fall_detected:
        return SystemState.WARNING, AlertType.FALL_DETECTED

    if power.battery_pct <= THRESHOLDS["BATTERY_CRITICAL_PERCENT"]:
        return SystemState.WARNING, AlertType.LOW_BATTERY

    if (
        vitals.heart_rate_bpm > 120
        or vitals.body_temp_c > 38.0
        or power.battery_pct <= THRESHOLDS["BATTERY_LOW_PERCENT"]
    ):
        return SystemState.WARNING, AlertType.PERIODIC_TELEMETRY

    # 6. Default Safe
    return SystemState.SAFE, AlertType.PERIODIC_TELEMETRY

"""Stable, minimal serial message contract between ADC firmware and laptop UI."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Reading:
    sensor_id: int
    device_ms: int
    raw_counts: int
    zeroed_counts: int


def parse_reading(line: str) -> Optional[Reading]:
    """Parse DATA,<sensor>,<device_ms>,<raw_counts>,<zeroed_counts>.

    Status, empty and malformed messages return None. Keep counts as integers:
    they cannot be labelled volts or microstrain without calibration.
    """
    parts = line.strip().split(",")
    if len(parts) != 5 or parts[0] != "DATA":
        return None
    try:
        sensor_id, device_ms, raw_counts, zeroed_counts = map(int, parts[1:])
    except ValueError:
        return None
    if sensor_id < 1 or device_ms < 0:
        return None
    return Reading(sensor_id, device_ms, raw_counts, zeroed_counts)

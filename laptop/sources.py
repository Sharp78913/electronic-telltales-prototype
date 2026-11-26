"""ADC streams: a real USB serial transport and a labelled simulation."""
import math
import random
import time
from typing import List

from protocol import Reading, parse_reading


class SerialSource:
    def __init__(self, port: str, baud: int = 115200):
        import serial
        self.connection = serial.Serial(port, baud, timeout=0.02)
        # Opening the port may reset an Arduino Uno. The caller can wait while
        # the firmware completes its initial zero measurement.
        self.status = f"Connected to {port}, waiting for samples"

    def poll(self) -> List[Reading]:
        results = []
        for _ in range(128):
            incoming = self.connection.readline()
            if not incoming:
                break
            line = incoming.decode("ascii", errors="replace").strip()
            reading = parse_reading(line)
            if reading is not None:
                results.append(reading)
            elif line.startswith("#"):
                self.status = line[1:]
        return results

    def zero(self) -> None:
        self.connection.write(b"ZERO\n")

    def close(self) -> None:
        self.connection.close()


class DemoSource:
    """Simulated counts for testing the software with no real ADC."""
    def __init__(self):
        self.start = time.monotonic()
        self.next_sample = 0.0
        self.status = "DEMO – synthetic sensor values, not measured data"
        self.rng = random.Random(14)
        self.offsets = {1: 41500, 2: 43000}

    def poll(self) -> List[Reading]:
        now = time.monotonic() - self.start
        result = []
        # 20 Hz per virtual sensor, capped to prevent catch-up flooding.
        for _ in range(20):
            if self.next_sample > now:
                break
            t = self.next_sample
            for sensor_id in (1, 2):
                raw = int(40000 + sensor_id * 1500
                          + 1100 * math.sin(2 * math.pi * (0.19 + sensor_id * 0.04) * t)
                          + 380 * math.sin(2 * math.pi * (1.3 + sensor_id * 0.2) * t)
                          + self.rng.gauss(0, 70))
                result.append(Reading(sensor_id, round(t * 1000), raw, raw - self.offsets[sensor_id]))
            self.next_sample += 0.05
        return result

    def zero(self) -> None:
        # In demo mode, use a stable synthetic baseline for illustration.
        self.offsets = {1: 41500, 2: 43000}
        self.status = "DEMO – baseline changed (synthetic data)"

    def close(self) -> None:
        pass

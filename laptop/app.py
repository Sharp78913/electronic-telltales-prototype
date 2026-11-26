"""Live strain-gauge counts from an Arduino (or a clearly labelled simulation)."""
import argparse
import csv
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

from sources import DemoSource, SerialSource


def options():
    p = argparse.ArgumentParser(description="Electronic Telltales live counts and CSV logger")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--port", help="Serial port, e.g. COM3 or /dev/ttyACM0")
    source.add_argument("--demo", action="store_true", help="Use SYNTHETIC readings without hardware")
    p.add_argument("--baud", type=int, default=115200, help="Arduino serial baud (default 115200)")
    p.add_argument("--mode", choices=("plot", "record"), default="plot")
    p.add_argument("--csv", type=Path, help="Write readings to this CSV path")
    p.add_argument("--duration", type=float, help="Recording time in seconds (record mode only)")
    p.add_argument("--window", type=float, default=20.0, help="Graph window length in seconds")
    args = p.parse_args()
    if args.mode == "record" and args.csv is None:
        p.error("--mode record requires --csv")
    if args.duration is not None and args.duration <= 0:
        p.error("--duration must be positive")
    return args


def main():
    args = options()
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
    source = DemoSource() if args.demo else SerialSource(args.port, args.baud)
    csv_file = None
    writer = None

    try:
        if args.csv:
            csv_file = args.csv.open("w", newline="", encoding="utf-8")
            writer = csv.writer(csv_file)
            writer.writerow(("host_utc", "sensor_id", "device_ms", "raw_counts", "zeroed_counts", "source"))

        def collect():
            readings = source.poll()
            for reading in readings:
                if writer:
                    writer.writerow((datetime.now(timezone.utc).isoformat(),
                                     reading.sensor_id, reading.device_ms,
                                     reading.raw_counts, reading.zeroed_counts,
                                     "demo" if args.demo else "arduino"))
            return readings

        print("DEMO data: simulated, NOT measured" if args.demo else f"Reading {args.port} at {args.baud} baud")
        print("Values are raw/zeroed ADC COUNTS, not voltage or strain.")
        if args.mode == "record":
            deadline = time.monotonic() + args.duration if args.duration else None
            counter = 0
            while deadline is None or time.monotonic() < deadline:
                counter += len(collect())
                time.sleep(0.03)
            print(f"Recorded {counter} sensor readings to {args.csv}")
            return

        # Matplotlib is only required for plotting; record-only mode also works
        # on headless systems without an interactive graphical environment.
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation
        from matplotlib.widgets import Button
        history = defaultdict(lambda: deque(maxlen=6000))
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.subplots_adjust(bottom=0.19)
        ax.set_xlabel("Device time (seconds)")
        ax.set_ylabel("Zeroed ADC counts – not calibrated")
        ax.grid(alpha=0.3)
        title_prefix = "DEMO (synthetic)" if args.demo else "HX711 prototype"
        ax.set_title(title_prefix)
        lines = {}

        def update(_frame):
            for reading in collect():
                history[reading.sensor_id].append((reading.device_ms / 1000,
                                                    reading.zeroed_counts))
            for sensor_id, values in history.items():
                if sensor_id not in lines:
                    line, = ax.plot([], [], label=f"Sensor {sensor_id}")
                    lines[sensor_id] = line
                    ax.legend(loc="upper right")
                if values:
                    max_x = values[-1][0]
                    xs = [x for x, _y in values if x >= max_x - args.window]
                    ys = [y for x, y in values if x >= max_x - args.window]
                    lines[sensor_id].set_data(xs, ys)
            if any(history.values()):
                ax.relim()
                ax.autoscale_view()
                last_x = max(v[-1][0] for v in history.values() if v)
                ax.set_xlim(max(0, last_x - args.window), max(args.window, last_x))
            fig.suptitle(source.status, fontsize=9)
            return list(lines.values())

        def do_zero(_event=None):
            source.zero()
            for samples in history.values():
                samples.clear()
            print("Requested ZERO: hold the beam stationary")

        def on_key(event):
            if event.key and event.key.lower() == "z":
                do_zero()

        button_area = fig.add_axes([0.80, 0.045, 0.16, 0.07])
        zero_button = Button(button_area, "Zero (Z)")
        zero_button.on_clicked(do_zero)
        fig.canvas.mpl_connect("key_press_event", on_key)
        # Keep references alive while the window is open.
        animation = FuncAnimation(fig, update, interval=100, cache_frame_data=False)
        _ = (animation, zero_button)
        plt.show()
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        if csv_file:
            csv_file.flush()
            csv_file.close()
        source.close()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(f"Error: {exc}")

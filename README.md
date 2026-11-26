# Electronic Sail Telltales – Sensor Prototype

Standalone bench-test repository for an **electronic sail telltale**. The first milestone is to read a foil strain gauge on a flexible beam using an HX711 and Arduino Uno, then display and log the changing signal on a laptop.

**Status:** prototype source prepared; **not yet verified with physical hardware**. Raw HX711 counts are not calibrated volts, strain, force or airflow measurements.

## Scope

- One strain gauge in a quarter-bridge, with three matching completion resistors
- Seeed Grove HX711 (or compatible HX711 breakout)
- Arduino Uno over USB serial
- Laptop live plot and CSV recording
- Demonstration mode that works without electronics
- Small, documented serial protocol ready for a future multi-sensor implementation

Not implemented yet: actual wind-direction/speed data, calibrated telltale angle, automatic steady/stalled airflow classification, wireless links or battery management. Those belong to later integration.

## Quick start – try the laptop software without hardware

Requires Python 3.10 or newer.

```powershell
cd electronic-telltales-prototype
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python laptop/app.py --demo
```

This opens a live two-sensor demonstration plot. **DEMO is clearly indicated** and generates synthetic data, not measurements.

To record demonstration data without showing a graph:

```powershell
python laptop/app.py --demo --mode record --csv data/demo.csv --duration 10
```

For macOS/Linux, activate with `source .venv/bin/activate` instead.

## Hardware quick start

1. Build the quarter bridge and wire the HX711 and Uno as described in [docs/wiring.md](docs/wiring.md). **Check the silkscreen on your specific breakout before powering it.**
2. Install the `HX711` Arduino library by **bogde** using Arduino IDE Library Manager.
3. Open [`arduino/telltale_hx711/telltale_hx711.ino`](arduino/telltale_hx711/telltale_hx711.ino) in Arduino IDE; select your Arduino Uno and upload.
4. Connect USB to the laptop and find the Arduino serial port (e.g. `COM3` on Windows).
5. Close Arduino Serial Monitor/Plotter (only one program can use the port at once), then run:

```powershell
python laptop/app.py --port COM3
```

Optional recording while plotting:

```powershell
python laptop/app.py --port COM3 --csv data/test_001.csv
```

Recording only:

```powershell
python laptop/app.py --port COM3 --mode record --csv data/test_002.csv
```

The firmware takes a small zero baseline at startup; keep the beam stationary during that period. In the graph window press **z** to re-zero while the sensor is stationary. For command-line recording, send `ZERO` with a serial terminal before starting the logger if a new zero is needed.

## First validation

- Confirm readings update when the beam is gently deflected both directions.
- Verify readings return close to baseline.
- Compare noise at rest with noise when the beam is touched/moved.
- Note whether the HX711 board operates at 10 or 80 samples per second (hardware-dependent).
- Only add a silicone tail and airflow test after beam bending is measurable.

See [docs/test-plan.md](docs/test-plan.md) for the test sequence.

## Repository layout

```text
arduino/telltale_hx711/    Arduino firmware
laptop/app.py              Laptop plot / CSV logger / demo mode
laptop/protocol.py         Text message parser
laptop/sources.py          Real serial and simulated data sources
docs/wiring.md             Exact first-prototype connections
docs/protocol.md           Serial protocol and integration boundary
docs/test-plan.md          Test stages and acceptance checks
docs/mechanical-notes.md   Physical prototype assumptions
tests/                     Parser and simulation smoke tests
```

## Integration later

Keep the firmware data acquisition independent from the laptop presentation. New ADCs (ADS1220), sensors and wireless transports can emit the same `DATA` records, while the plotting/logger layer remains reusable. See [docs/protocol.md](docs/protocol.md).

## Hardware and library references

- [Seeed Grove ADC for Load Cell (HX711)](https://wiki.seeedstudio.com/grove_adc_for_load_cell_hx711/)
- [bogde/HX711 Arduino library](https://github.com/bogde/HX711)
- [RS strain gauge 223-6476](https://ie.rs-online.com/web/p/strain-gauges/2236476)

## Before publishing

The repository is intentionally **not assigned an open-source licence** yet. Choose a licence if you want others to have permission to reuse the code. Do not commit personal data, serial-port recordings or credentials.

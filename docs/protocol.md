# Sensor serial protocol (version 1)

UTF-8/ASCII text, **115200 baud**, newline-terminated. No calibration implied.

## Data records

```text
DATA,1,12345,840000,-315
```

Fields: `DATA`, `sensor_id` (integer >= 1), `device_ms` (`millis()` timestamp), `raw_counts` (signed HX711 counts), `zeroed_counts` (`raw_counts - zero_offset`).

The Arduino `millis()` counter can wrap after approximately 49.7 days. In software that runs longer, detect wrap and maintain elapsed time separately. Future multi-sensor firmware can send `DATA,2,...` lines with different sensor IDs; the laptop parser already supports this.

## Status and control

Lines beginning with `#` contain status, for example:

```text
#INFO,protocol=1,adc=HX711,sensors=1,baud=115200,units=counts
#EVENT,ZERO_BEGIN
#EVENT,ZERO_OK,839900
#WARN,HX711_NOT_READY_CHECK_POWER_AND_WIRING
```

Commands from laptop to Arduino (case-sensitive, newline-terminated):

- `ZERO` – collect 12 stationary readings and update baseline
- `PING` – reply `#PONG`
- `INFO` – reply with device description

There is intentionally no conversion to µV or microstrain. Such conversion requires characterisation of the actual bridge excitation, gain and offset, followed by mechanical calibration. Airflow condition classification is **not** established.

## Integration boundary

The laptop app consumes `Reading` objects. Keep firmware and transport hardware-specific, and use the same schema when replacing HX711 with ADS1220 or moving to wireless communication. A final helm display should consume **validated interpreted values**, not turn raw counts directly into unverified attached/stalled labels.

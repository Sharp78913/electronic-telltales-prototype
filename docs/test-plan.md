# Prototype test checklist

## Stage 1 – Electronic readout

- [ ] Record gauge model and resistance, ADC model, Arduino board and wiring arrangement
- [ ] Confirm `#INFO` and `#EVENT,ZERO_OK` over 115200-baud serial
- [ ] Record zeroed counts with beam stationary for at least 30 seconds
- [ ] Gently bend one direction and confirm repeatable sign and magnitude
- [ ] Bend opposite direction and confirm the sign reverses
- [ ] Release beam and check return close to zero

## Stage 2 – Mechanical / airflow tests

- [ ] Repeat for candidate beam materials and thicknesses
- [ ] Record the exposed beam length, clamped length and tail shape
- [ ] Compare with and without silicone tail
- [ ] Test in still air and controlled fan airflow
- [ ] Record possible gravitational baseline shifts when changing sensor orientation
- [ ] Check whether the beam survives repetitive bending without drift or damage

## Stage 3 – Laptop/data

- [ ] Use the live graph to compare raw time histories
- [ ] Record CSV and open in spreadsheet or Python
- [ ] Measure actual sample rate from device timestamps
- [ ] Look for missing data, saturation and electrical noise
- [ ] If required, move to a faster ADC for flutter investigations

**Acceptance for the first prototype:** demonstrable, repeatable change in raw ADC counts with controlled bending, with readings recorded by the laptop. Do not claim airflow sensing accuracy until wind/tail calibration is complete.

# First prototype wiring – quarter bridge + HX711 + Uno

**Hardware:** 1 × 350 Ω single-element foil strain gauge, 3 × nominally 350 Ω precision bridge-completion resistors, Grove HX711 board (or pin-equivalent breakout), Arduino Uno, USB cable, breadboard, secure gauge leads.

## 1. Complete the bridge

An HX711 breakout expects a four-terminal *bridge*. A two-wire strain gauge alone is not a complete load cell.

```text
                       E+ (excitation positive)
                        +-----------------+
                        |                 |
                    [ RG 350Ω ]       [ R1 350Ω ]
                        |                 |
                        +-- A+       A- --+
                        |                 |
                    [ R2 350Ω ]       [ R3 350Ω ]
                        |                 |
                        +-----------------+
                       E- (excitation return)
```

- `RG`: active gauge glued to the beam; orientation along the beam's length (X).
- `R1`, `R2`, `R3`: precision resistors, nominally matching the gauge.
- The two *middle nodes* (`A+` and `A-`) are not electrically joined to each other.
- Use only the HX711 board's **E+ / E-** to energise the bridge, not a second independent power source.

A mismatched bridge can create a large initial offset. The HX711 input range is small; if readings saturate, check the bridge topology, resistor values and connections before software calibration. Contact resistance and temperature drift matter at these signal levels.

## 2. HX711 screw terminal to bridge

| Bridge node | Typical Seeed terminal | Function |
|---|---|---|
| E+ | E+ | Excitation positive |
| E- | E- | Excitation negative |
| A+ | INA+ / A+ | Channel A differential positive |
| A- | INA- / A- | Channel A differential negative |

Confirm exact names and physical pin positions on the specific module. Swapping A+ and A- reverses the sign of bending readings; crossing excitation and analogue inputs is **not** equivalent.

## 3. Grove connector to Arduino Uno

A 4-pin Grove-to-male-jumper lead can connect to the Uno headers.

| Grove HX711 connector label | Arduino Uno |
|---|---|
| GND | GND |
| VCC | 5V |
| DOUT | D2 |
| PSCK / SCK | D3 |

**Match the labels, not the cable colour order.** The HX711 interface is not SPI or I²C. The board normally uses a synchronous data/clock pair. The Uno connects to the laptop through its regular USB port.

## 4. Assembly notes

- Use the breadboard for bridge completion and the module connections initially; secure the fragile gauge leads using a suitable terminal connection/strain relief.
- Keep bridge and analogue wiring short; move it to a soldered carrier board if loose breadboard contacts cause noise.
- Build the bridge using four resistors first if you want an electrical sanity check, then replace `RG` with the gauge.
- Keep the beam stationary while collecting its zero reference.
- Test with **gentle controlled bending** before applying airflow; do not use the gauge itself as a mechanical connector.
- Seeed modules use 10 or 80 samples/second, with the selected rate dependent on the *board hardware*. Do not assume the firmware can change the RATE pin.

## Reference

Seeed official documentation: https://wiki.seeedstudio.com/grove_adc_for_load_cell_hx711/

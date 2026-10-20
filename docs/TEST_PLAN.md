# Test Plan: Arduino Curve Tracer

Version 1.0 (Oct 2026). Scope: two-terminal devices (diodes, LEDs). Targets below were set by the author as design goals, then checked against measured data.

## 1. Requirements

| ID | Requirement | Target |
|---|---|---|
| R1 | Sweep range | DAC codes 0 to 4095 in steps of 16 (256 points, about 20 mV per point) |
| R2 | Current protection | Sweep stops when measured current exceeds 8 mA; no logged point above 9 mA |
| R3 | DAC accuracy (unloaded) | Measured output within 0.05 V of commanded value, 0 to 4.9 V |
| R4 | Repeatability | Voltage at 1 mA varies by 2 mV or less across 3 consecutive sweeps of the same device |
| R5 | Data output | Each sweep produces a CSV (`code,v_src,v_dut,i_ma`) and linear + semilog plots |
| R6 | Analysis | Script reports ideality factor, saturation current, and voltage at 1 mA per run |

## 2. Procedures

**P1: DAC verification (R3).** Connect DAC VOUT to Uno A1 only. Upload the check sketch, command codes 0, 512, 1024, 2048, 3072, 4000, and compare the A1 reading with code x 5 V / 4095.

**P2: Single sweep (R1, R2, R5).** Wire DAC VOUT to the 560 ohm resistor, then to the device (anode) and A0, with A1 on VOUT and the device cathode to GND. Upload `curve_tracer_v1.ino`, close the Serial Monitor, and run `python plot_iv.py <port> <name>`.

**P3: Repeatability (R4, R6).** Run P2 three times back to back with names `<device>_run1..3`, then run `python analyze_iv.py <run1> <run2> <run3>`.

## 3. Pass/fail criteria

A requirement passes when the measured value meets its target. Any failure is recorded in section 4 with a note.

## 4. Results (Oct 2026)

| ID | Result | Status |
|---|---|---|
| R1 | 256 points per sweep, codes 0 to 4080 | Pass |
| R2 | Highest logged current 7.2 mA (diode), 5.4 mA (LED); the 8 mA cutoff was never reached, so the cutoff has NOT been exercised in a test | Not verified |
| R3 | Maximum difference 0.02 V (4.88 V commanded, 4.90 V measured) | Pass |
| R4 | Voltage at 1 mA spread: 0.5 mV (1N4007), 1.1 mV (red LED) | Pass |
| R5 | CSV and plots generated for every run (see repo root) | Pass |
| R6 | 1N4007: n 1.73 to 1.74, Is about 1.6e-9 A. Red LED: n 2.32 to 2.35, Is about 6e-16 to 8e-16 A | Pass |

## 5. Known limitations

- ADC step is about 4.9 mV, so one step of current is about 9 microamps; currents below roughly 10 microamps are noise.
- Under load the DAC output tops out near 4.7 V because the Uno's 5 V rail sags at about 7 mA.
- Single device of each type, single session, back-to-back runs only (short-term repeatability).
- Temperature assumed to be 25 C in the fit; not measured.
- No calibrated reference instrument was used, so absolute accuracy is unknown.

## 6. Planned follow-up

- Exercise the 8 mA cutoff with a lower-resistance load or a device that conducts earlier.
- Compare the 1N4007 curve against an LTspice model or datasheet curve.
- Repeat across multiple sessions and devices.

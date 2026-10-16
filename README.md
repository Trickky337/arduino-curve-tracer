# Arduino Curve Tracer

An automated I-V curve tracer for diodes and LEDs (BJTs and MOSFETs planned), built with an Arduino Uno, an Adafruit MCP4725 12-bit DAC, and Python analysis tools.

## Status: working prototype

The tracer produces clean, repeatable I-V sweeps of a 1N4007 silicon diode. LED sweeps and transistor support are next.

![1N4007 I-V curve](1N4007.png)

## Results (1N4007, three back-to-back sweeps)

| Run | Ideality factor n | Saturation current Is | Voltage at 1 mA |
|---|---|---|---|
| 1 | 1.74 | 1.67e-09 A | 0.5926 V |
| 2 | 1.73 | 1.60e-09 A | 0.5931 V |
| 3 | 1.74 | 1.69e-09 A | 0.5927 V |

- The voltage at 1 mA varied by 0.5 mV across the three runs (short-term repeatability).
- The semilog plot is a straight line from about 0.4 V upward, as the Shockley equation predicts.
- Fit details: Shockley equation fitted to 0.05 to 7 mA, assuming room temperature of about 25 C (thermal voltage 25.69 mV). Results are from one diode in one session.

![Repeatability and Shockley fit](repeatability.png)

Known limits: the ADC step is about 5 mV, so currents below roughly 10 microamps are noise. The DAC output tops out near 4.7 V under load because the Uno's 5 V rail sags at about 7 mA.

![Breadboard setup](setup.webp)

## How it works

The DAC output drives a 560 ohm sense resistor in series with the device under test (DUT), then to ground.

- A1 reads the voltage at the top of the resistor (V_src).
- A0 reads the voltage across the DUT (V_dut).
- Current: I = (V_src - V_dut) / R_SENSE
- The sweep stops automatically if current exceeds 8 mA.

The DAC was verified by reading its unloaded output back with the Uno's ADC: measured voltage matched the commanded value within about 0.02 V from 0 to 4.9 V.

## Hardware

- Arduino Uno R3
- Adafruit MCP4725 12-bit DAC (I2C: A4 = SDA, A5 = SCL)
- 560 ohm sense resistor
- Diode / LED under test, breadboard, jumper wires

## Software

- `curve_tracer_v1/curve_tracer_v1.ino`: Arduino firmware. Send `s` over serial (115200 baud) to run one sweep. Output is CSV: `code,v_src,v_dut,i_ma`.
- `plot_iv.py`: triggers a sweep, saves a CSV, and plots linear and semilog I-V curves. Usage: `python plot_iv.py COM4 1N4007`
- `analyze_iv.py`: overlays repeated sweeps and fits the Shockley equation. Usage: `python analyze_iv.py run1 run2 run3`

Requires Python with `pyserial`, `matplotlib`, and `numpy`.

## Roadmap

- [x] Wire up Uno, DAC, sense resistor, and diode
- [x] Firmware and plotting script written
- [x] DAC output verified against commanded codes
- [x] First clean I-V sweep of a 1N4007 diode
- [x] Repeatability tests (three sweeps, same diode)
- [x] Shockley fit for ideality factor and saturation current
- [ ] LED sweeps
- [ ] Compare against a datasheet or LTspice model
- [ ] Add BJT / MOSFET support

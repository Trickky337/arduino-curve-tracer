# Arduino Curve Tracer

An automated I-V curve tracer for diodes and LEDs (BJTs and MOSFETs planned), built with an Arduino Uno, an Adafruit MCP4725 12-bit DAC, and a Python plotting tool.

## Status: working prototype

The tracer produces clean I-V sweeps of a 1N4007 silicon diode. Repeatability tests, LED sweeps, and transistor support are next.

![1N4007 I-V curve](1N4007.png)

First measured sweep (1N4007): current reaches about 1 mA near 0.6 V and 7 mA at 0.68 V. The semilog plot is a straight line from about 0.4 V upward, as the Shockley equation predicts. A rough estimate of the ideality factor from the slope is about 1.6 to 1.7 (a proper curve fit is still to do). Raw data is in `1N4007.csv`.

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
- `plot_iv.py`: Python tool (pyserial, matplotlib) that triggers a sweep, saves a CSV, and plots linear and semilog I-V curves.

Usage: `python plot_iv.py <serial-port> <device-name>`, for example `python plot_iv.py COM4 1N4007`.

## Roadmap

- [x] Wire up Uno, DAC, sense resistor, and diode
- [x] Firmware and plotting script written
- [x] I2C communication with the DAC verified
- [x] DAC output verified against commanded codes
- [x] First clean I-V sweep of a 1N4007 diode
- [ ] Repeatability tests (multiple sweeps, same diode)
- [ ] Fit the Shockley equation to extract ideality factor and saturation current
- [ ] LED sweeps
- [ ] Add BJT / MOSFET support

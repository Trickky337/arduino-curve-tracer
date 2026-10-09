# arduino-curve-tracer
# Arduino Curve Tracer

**Status: in development.** The firmware and plotting tool are being built and tested. No measurements have been recorded yet; results will be added here as they are collected.

## What it is
An automated component curve tracer that measures the I-V characteristic of diodes and LEDs (BJTs and MOSFETs planned). An Arduino Uno steps a 12-bit MCP4725 DAC through a sense resistor into the device under test, measures the voltage on both sides of the resistor, and computes the current with Ohm's law. A Python script logs each sweep to CSV and plots it.

## Design
- DAC output -> 560 ohm sense resistor -> device under test -> GND
- Current = (V_source - V_device) / R_sense
- Sweep stops automatically if current exceeds a set limit, to protect the part
- Voltages read with the Uno's 10-bit ADC (ADS1115 16-bit ADC planned as an upgrade)

## Hardware
- Arduino Uno R3
- Adafruit MCP4725 12-bit I2C DAC
- 560 ohm sense resistor
- Breadboard, jumper wires, diodes and LEDs

## Software
- Arduino C/C++ firmware (Adafruit MCP4725 library)
- Python 3 with pyserial and matplotlib (linear and semilog I-V plots)

## Roadmap
- [x] Arduino IDE and library setup
- [x] Wire the DAC and confirm it over I2C
- [x] First diode sweep and plot
- [ ] LED color comparison
- [ ] Repeatability test (repeat sweeps, compare)
- [ ] Calibrate resistor value and 5 V reference against a multimeter
- [ ] Compare results to datasheet values
- [ ] Add BJT and MOSFET tracing
- [ ] Add plots and wiring diagram to this README

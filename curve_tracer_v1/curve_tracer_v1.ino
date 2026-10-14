// Curve Tracer V1: Arduino Uno + MCP4725 DAC + Uno ADC
// Wiring:
//   MCP4725 VIN -> 5V, GND -> GND, SDA -> A4, SCL -> A5
//   MCP4725 VOUT -> A1 and one end of R_SENSE
//   R_SENSE other end -> device anode and A0
//   device cathode -> GND
// Send 's' over serial (115200 baud) to run one sweep.
// Output: START, header, CSV lines (code,v_src,v_dut,i_ma), END

#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac;

const float R_SENSE = 560.0;     // ohms: update with measured value
const float VREF = 5.00;         // volts: update with measured 5V pin
const float I_LIMIT_MA = 8.0;    // stop the sweep above this current
const int STEP = 16;             // DAC codes per step (4096 / 16 = 256 points)
const int AVG = 32;              // ADC samples averaged per reading

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setWireTimeout(3000, true);
  if (!dac.begin(0x62)) {        // try 0x63 if the scanner shows that address
    Serial.println("MCP4725 not found");
    while (1);
  }
  dac.setVoltage(0, false);
  delay(500);
  Serial.println("READY");
}

void loop() {
  if (Serial.available() && Serial.read() == 's') sweep();
}

float readVolts(uint8_t pin) {
  analogRead(pin);               // throw away the first reading after a mux switch
  delayMicroseconds(200);
  long sum = 0;
  for (int i = 0; i < AVG; i++) sum += analogRead(pin);
  return (sum / (float)AVG) * VREF / 1023.0;
}

void sweep() {
  Serial.println("START");
  Serial.println("code,v_src,v_dut,i_ma");
  for (int code = 0; code <= 4095; code += STEP) {
    dac.setVoltage(code, false);
    delay(5);
    float v_dut = readVolts(A0);
    float v_src = readVolts(A1);
    float i_ma = (v_src - v_dut) / R_SENSE * 1000.0;
    Serial.print(code);   Serial.print(',');
    Serial.print(v_src, 4); Serial.print(',');
    Serial.print(v_dut, 4); Serial.print(',');
    Serial.println(i_ma, 4);
    if (i_ma > I_LIMIT_MA) break;
  }
  dac.setVoltage(0, false);
  Serial.println("END");
}

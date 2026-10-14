"""Run one sweep, save CSV, plot I-V.  Usage:  python plot_iv.py COM3 1N4148_01
(on Mac/Linux the port looks like /dev/ttyACM0 or /dev/cu.usbmodem1101)"""
import sys, time, csv
import serial
import matplotlib.pyplot as plt

port, name = sys.argv[1], sys.argv[2]
ser = serial.Serial(port, 115200, timeout=10)
time.sleep(2.5)                       # the Uno resets when the port opens
ser.reset_input_buffer()
while ser.readline().decode(errors="ignore").strip() != "READY":
    pass
ser.write(b"s")

rows, started = [], False
while True:
    line = ser.readline().decode(errors="ignore").strip()
    if line == "START":
        started = True
    elif line == "END" or line == "":
        break
    elif started and line[0].isdigit():
        code, vs, vd, i = line.split(",")
        rows.append((int(code), float(vs), float(vd), float(i)))
ser.close()

with open(f"{name}.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["code", "v_src", "v_dut", "i_ma"])
    w.writerows(rows)

v = [r[2] for r in rows]
i = [max(r[3], 1e-4) for r in rows]   # floor so the log plot works
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(v, i); ax[0].set_xlabel("Device voltage (V)"); ax[0].set_ylabel("Current (mA)"); ax[0].set_title(name)
ax[1].semilogy(v, i); ax[1].set_xlabel("Device voltage (V)"); ax[1].set_ylabel("Current (mA, log)")
for a in ax: a.grid(True)
plt.tight_layout(); plt.savefig(f"{name}.png", dpi=150); plt.show()
print(f"Saved {name}.csv and {name}.png with {len(rows)} points")

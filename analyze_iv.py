"""Overlay repeated sweeps and fit the Shockley equation.
Usage: python analyze_iv.py 1N4007_run1 1N4007_run2 1N4007_run3"""
import csv, sys
import numpy as np
import matplotlib.pyplot as plt

VT = 0.02569                      # thermal voltage kT/q at about 25 C (volts)
FIT_MIN, FIT_MAX = 0.05, 7.0      # mA: above ADC noise, below the sweep end
names = sys.argv[1:]

def load(name):
    v, i = [], []
    with open(f"{name}.csv") as f:
        for row in csv.DictReader(f):
            v.append(float(row["v_dut"]))
            i.append(float(row["i_ma"]))
    return np.array(v), np.array(i)

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ns, v1s = [], []
print(f"{'run':<14}{'n':>7}{'Is (A)':>14}{'V @ 1 mA':>12}")
for k, name in enumerate(names):
    v, i = load(name)
    m = (i > FIT_MIN) & (i < FIT_MAX)
    slope, intercept = np.polyfit(v[m], np.log(i[m]), 1)
    n = 1.0 / (slope * VT)
    Is = np.exp(intercept) * 1e-3
    idx = np.argsort(i)
    v1 = float(np.interp(1.0, i[idx], v[idx]))
    ns.append(n)
    v1s.append(v1)
    print(f"{name:<14}{n:>7.2f}{Is:>14.2e}{v1:>12.4f}")
    ax[0].semilogy(v, np.maximum(i, 1e-4), label=name)
    if k == 0:
        ax[1].semilogy(v, np.maximum(i, 1e-4), ".", label=f"{name} data")
        vf = np.linspace(v[m].min(), v[m].max(), 50)
        ax[1].semilogy(vf, np.exp(intercept + slope * vf), "r-", label=f"fit: n = {n:.2f}")

print(f"\nIdeality factor n: mean {np.mean(ns):.2f}, spread {max(ns)-min(ns):.2f}")
print(f"Voltage at 1 mA: mean {np.mean(v1s):.4f} V, spread {(max(v1s)-min(v1s))*1000:.1f} mV")

ax[0].set_title("Repeatability: overlaid sweeps")
ax[1].set_title("Shockley fit (first run)")
for a in ax:
    a.set_xlabel("Device voltage (V)")
    a.set_ylabel("Current (mA, log)")
    a.grid(True)
    a.legend()
plt.tight_layout()
plt.savefig("repeatability.png", dpi=150)
plt.show()

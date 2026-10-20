"""Automated repeatability test that writes a report.

Live (board connected):
    python run_test.py --name 1N4007 --port COM4 --runs 3
Offline (re-analyze saved sweeps):
    python run_test.py --name 1N4007 --csv 1N4007_run1.csv 1N4007_run2.csv 1N4007_run3.csv
"""
import argparse
import csv
import datetime
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

VT = 0.02569                   # thermal voltage at about 25 C (V)
FIT_MIN, FIT_MAX = 0.05, 7.0   # mA, range used for the Shockley fit
I_LIMIT_MA = 8.0               # firmware cutoff
I_MAX_LOGGED_MA = 9.0          # R2: no logged point above this
SPREAD_LIMIT_MV = 2.0          # R4: spread of voltage at 1 mA


def sweep_once(ser):
    ser.reset_input_buffer()
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
    if not rows:
        raise RuntimeError("No data received. Is the sweep sketch uploaded and the Serial Monitor closed?")
    return rows


def save_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "v_src", "v_dut", "i_ma"])
        w.writerows(rows)


def load_csv(path):
    with open(path) as f:
        return [(int(r["code"]), float(r["v_src"]), float(r["v_dut"]), float(r["i_ma"]))
                for r in csv.DictReader(f)]


def analyze(rows):
    a = np.array(rows)
    v, i = a[:, 2], a[:, 3]
    m = (i > FIT_MIN) & (i < FIT_MAX)
    if m.sum() < 5:
        raise RuntimeError("Too few points in the fit range.")
    slope, intercept = np.polyfit(v[m], np.log(i[m]), 1)
    idx = np.argsort(i)
    return {
        "n": 1.0 / (slope * VT),
        "Is": float(np.exp(intercept) * 1e-3),
        "v1": float(np.interp(1.0, i[idx], v[idx])),
        "imax": float(i.max()),
        "points": len(rows),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--port")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--csv", nargs="+")
    args = p.parse_args()

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("reports", exist_ok=True)
    runs = []

    if args.csv:
        for path in args.csv:
            runs.append((os.path.splitext(os.path.basename(path))[0], load_csv(path)))
    elif args.port:
        import serial
        os.makedirs("data", exist_ok=True)
        ser = serial.Serial(args.port, 115200, timeout=10)
        time.sleep(2.5)
        for k in range(1, args.runs + 1):
            print(f"Sweep {k} of {args.runs} ...")
            rows = sweep_once(ser)
            label = f"{args.name}_{stamp}_run{k}"
            save_csv(os.path.join("data", label + ".csv"), rows)
            runs.append((label, rows))
            time.sleep(1.0)
        ser.close()
    else:
        p.error("give --port for a live test or --csv for saved sweeps")

    results = [(label, analyze(rows)) for label, rows in runs]
    v1s = [r["v1"] for _, r in results]
    ns = [r["n"] for _, r in results]
    spread_mv = (max(v1s) - min(v1s)) * 1000
    imax = max(r["imax"] for _, r in results)

    r4 = "PASS" if spread_mv <= SPREAD_LIMIT_MV else "FAIL"
    if imax > I_MAX_LOGGED_MA:
        r2 = "FAIL"
    elif imax > I_LIMIT_MA:
        r2 = "PASS (cutoff triggered)"
    else:
        r2 = "NOT VERIFIED (sweep ended below 8 mA, so the cutoff was not exercised)"

    fig, ax = plt.subplots(figsize=(6, 4))
    for label, rows in runs:
        a = np.array(rows)
        ax.semilogy(a[:, 2], np.maximum(a[:, 3], 1e-4), label=label)
    ax.set_xlabel("Device voltage (V)")
    ax.set_ylabel("Current (mA, log)")
    ax.set_title(f"{args.name}: overlaid sweeps")
    ax.grid(True)
    ax.legend(fontsize=6)
    fig.tight_layout()
    png = f"reports/{args.name}_{stamp}.png"
    fig.savefig(png, dpi=150)

    lines = [
        f"# Test report: {args.name}", "",
        f"Generated {datetime.datetime.now():%Y-%m-%d %H:%M}. {len(runs)} sweeps.", "",
        "| Run | Points | n | Is (A) | V at 1 mA (V) | Max current (mA) |",
        "|---|---|---|---|---|---|",
    ]
    for label, r in results:
        lines.append(f"| {label} | {r['points']} | {r['n']:.2f} | {r['Is']:.2e} | {r['v1']:.4f} | {r['imax']:.2f} |")
    lines += [
        "", "## Summary", "",
        f"- Ideality factor n: mean {np.mean(ns):.2f}, spread {max(ns) - min(ns):.2f}",
        f"- Voltage at 1 mA: mean {np.mean(v1s):.4f} V, spread {spread_mv:.1f} mV",
        "", "## Requirement checks (see docs/TEST_PLAN.md)", "",
        f"- R4 repeatability (spread <= {SPREAD_LIMIT_MV} mV): **{r4}** ({spread_mv:.1f} mV)",
        f"- R2 current protection (max logged current {imax:.2f} mA): **{r2}**",
        "", f"![overlay]({os.path.basename(png)})", "",
        "Fit assumes 25 C. Short-term repeatability only; single device.",
    ]
    md = f"reports/{args.name}_{stamp}.md"
    with open(md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {md} and {png}")


if __name__ == "__main__":
    main()

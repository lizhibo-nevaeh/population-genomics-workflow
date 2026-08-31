#!/usr/bin/env python3
"""Plot PSMC population-size trajectories directly from PSMC output.

Scaling follows the PSMC documentation:
N0 = theta0 / (4 * mutation_rate * skip)
T  = 2 * N0 * t_k * generation_time
Ne = N0 * lambda_k
"""
import argparse
import re
import numpy as np
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument("--psmc", required=True, help="PSMC output or combined main+bootstrap PSMC file")
p.add_argument("--mutation-rate", type=float, required=True, help="Per-site per-generation mutation rate")
p.add_argument("--generation-time", type=float, required=True, help="Years per generation")
p.add_argument("--skip", type=float, default=100.0, help="Bin size used when generating PSMC input; fq2psmcfa default is 100")
p.add_argument("--iteration", type=int, help="Iteration to plot; default is the maximum RD value found")
p.add_argument("--output", default="psmc.png")
p.add_argument("--title", default="PSMC demographic history")
p.add_argument("--min-years", type=float, default=0.0)
a = p.parse_args()

blocks = []
current = None
with open(a.psmc) as fh:
    for raw in fh:
        line = raw.strip()
        if line.startswith("RD\t") or line.startswith("RD "):
            parts = line.split()
            current = {"rd": int(parts[1]), "theta": None, "dt": 0.0, "rs": []}
            blocks.append(current)
        elif current is not None and (line.startswith("TR\t") or line.startswith("TR ")):
            parts = line.split()
            current["theta"] = float(parts[1])
        elif current is not None and (line.startswith("DT\t") or line.startswith("DT ")):
            parts = line.split()
            current["dt"] = float(parts[1])
        elif current is not None and (line.startswith("RS\t") or line.startswith("RS ")):
            parts = line.split()
            if len(parts) >= 4:
                current["rs"].append((int(parts[1]), float(parts[2]), float(parts[3])))

valid = [b for b in blocks if b["theta"] is not None and b["rs"]]
if not valid:
    raise SystemExit("No complete RD/TR/RS PSMC blocks found")
iteration = a.iteration if a.iteration is not None else max(b["rd"] for b in valid)
curves = [b for b in valid if b["rd"] == iteration]
if not curves:
    raise SystemExit(f"No PSMC block found for iteration {iteration}")

def scale_curve(block):
    n0 = block["theta"] / (4.0 * a.mutation_rate * a.skip)
    t, ne = [], []
    for _, tk, lam in block["rs"]:
        years = 2.0 * n0 * (tk + block["dt"]) * a.generation_time
        size = n0 * lam
        if years >= a.min_years:
            t.append(years)
            ne.append(size)
    return np.asarray(t), np.asarray(ne)

fig, ax = plt.subplots(figsize=(7.4, 5.2))
main_t, main_ne = scale_curve(curves[0])
line = ax.step(main_t, main_ne, where="post", linewidth=2.0, label="Estimate")[0]
main_color = line.get_color()
for block in curves[1:]:
    t, ne = scale_curve(block)
    ax.step(t, ne, where="post", linewidth=0.7, alpha=0.15, color=main_color)

ax.set_xscale("log")
ax.set_xlabel("Years before present")
ax.set_ylabel("Effective population size (Ne)")
ax.set_title(a.title)
if len(curves) > 1:
    ax.text(0.99, 0.02, f"Bootstrap curves: {len(curves)-1}", transform=ax.transAxes, ha="right", va="bottom", fontsize=8)
fig.tight_layout()
fig.savefig(a.output, dpi=240, bbox_inches="tight")

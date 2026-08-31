#!/usr/bin/env python3
"""Plot LD decay directly from PopLDdecay statistic files.

Supports the common PopLDdecay summary format
  #Dist Mean_r^2 Mean_D' Sum_r^2 Sum_D' NumberPairs
and count-based formats in which rows contain distance, r^2 and count.
"""
import argparse
import gzip
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument("--inputs", nargs="+", required=True, help="One or more PopLDdecay .stat/.stat.gz files")
p.add_argument("--labels", nargs="*", help="Labels matching --inputs")
p.add_argument("--output", default="ld_decay.png")
p.add_argument("--max-kb", type=float, help="Optional maximum plotted distance in kb")
p.add_argument("--bin-bp", type=int, default=1000, help="Bin size for count-based PopLDdecay output")
p.add_argument("--title", default="LD decay")
a = p.parse_args()

if a.labels and len(a.labels) != len(a.inputs):
    raise SystemExit("--labels must have the same number of values as --inputs")
labels = a.labels or [Path(x).name.replace(".stat.gz", "").replace(".stat", "") for x in a.inputs]

def read_first_line(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt") as fh:
        return fh.readline().strip()

def load_curve(path):
    header = read_first_line(path)
    cols = header.lstrip("#").split()
    df = pd.read_csv(path, sep=r"\s+", comment="#", header=None, compression="infer")
    if "Mean_r^2" in cols and len(cols) == df.shape[1]:
        df.columns = cols
        out = df[["Dist", "Mean_r^2"]].copy()
        out.columns = ["dist_bp", "mean_r2"]
        return out

    if df.shape[1] < 3:
        raise SystemExit(f"Unsupported PopLDdecay format: {path}")

    # Count-based forms: Dist, r2, count [, Dprime, count]
    z = df.iloc[:, :3].copy()
    z.columns = ["dist_bp", "r2", "count"]
    z = z.apply(pd.to_numeric, errors="coerce").dropna()
    z = z[(z["dist_bp"] >= 0) & (z["count"] > 0)]
    z["bin"] = (z["dist_bp"] // a.bin_bp) * a.bin_bp
    z["weighted"] = z["r2"] * z["count"]
    out = z.groupby("bin", as_index=False).agg(weighted=("weighted", "sum"), count=("count", "sum"))
    out["mean_r2"] = out["weighted"] / out["count"]
    out = out.rename(columns={"bin": "dist_bp"})
    return out[["dist_bp", "mean_r2"]]

fig, ax = plt.subplots(figsize=(7.2, 5.1))
for path, label in zip(a.inputs, labels):
    d = load_curve(path)
    d["dist_kb"] = d["dist_bp"] / 1000.0
    if a.max_kb is not None:
        d = d[d["dist_kb"] <= a.max_kb]
    ax.plot(d["dist_kb"], d["mean_r2"], linewidth=1.6, label=label)

ax.set_xlabel("Distance (kb)")
ax.set_ylabel("Mean r²")
ax.set_title(a.title)
if len(a.inputs) > 1:
    ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(a.output, dpi=240, bbox_inches="tight")

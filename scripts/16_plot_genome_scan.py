#!/usr/bin/env python3
"""Chromosome-by-chromosome genome-scan plot for window statistics."""
import argparse
import pandas as pd
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--chrom-col", required=True)
p.add_argument("--pos-col", required=True)
p.add_argument("--value-col", required=True)
p.add_argument("--sep", default="\t")
p.add_argument("--output", default="genome_scan.png")
p.add_argument("--ylabel", default="Statistic")
p.add_argument("--title", default="Genome scan")
p.add_argument("--quantile", type=float, help="Optional upper quantile threshold, e.g. 0.99")
a = p.parse_args()

try:
    df = pd.read_csv(a.input, sep=a.sep, comment="#")
except Exception:
    df = pd.read_csv(a.input, sep=r"\s+", comment="#")
for c in (a.chrom_col, a.pos_col, a.value_col):
    if c not in df.columns:
        raise SystemExit(f"Column not found: {c}")

df = df[[a.chrom_col, a.pos_col, a.value_col]].copy()
df[a.pos_col] = pd.to_numeric(df[a.pos_col], errors="coerce")
df[a.value_col] = pd.to_numeric(df[a.value_col], errors="coerce")
df = df.dropna()

chroms = list(dict.fromkeys(df[a.chrom_col].astype(str)))
offset = 0.0
centers, parts = [], []
for i, chrom in enumerate(chroms):
    d = df[df[a.chrom_col].astype(str) == chrom].copy().sort_values(a.pos_col)
    d["plot_x"] = d[a.pos_col] + offset
    parts.append((i, d))
    centers.append((d["plot_x"].min() + d["plot_x"].max()) / 2)
    span = max(float(d[a.pos_col].max()), 1.0)
    offset = float(d["plot_x"].max()) + max(1.0, span * 0.02)

fig, ax = plt.subplots(figsize=(11.5, 4.8))
for i, d in parts:
    ax.scatter(d["plot_x"], d[a.value_col], s=6, alpha=0.75)

if a.quantile is not None:
    if not 0 < a.quantile < 1:
        raise SystemExit("--quantile must be between 0 and 1")
    threshold = df[a.value_col].quantile(a.quantile)
    ax.axhline(threshold, linestyle="--", linewidth=1.0, label=f"q={a.quantile:g}: {threshold:.4g}")
    ax.legend(frameon=False, fontsize=8)

ax.set_xticks(centers)
ax.set_xticklabels(chroms, rotation=45, ha="right", fontsize=8)
ax.set_xlabel("Chromosome / scaffold")
ax.set_ylabel(a.ylabel)
ax.set_title(a.title)
fig.tight_layout()
fig.savefig(a.output, dpi=240, bbox_inches="tight")

#!/usr/bin/env python3
"""Plot PC1 vs PC2 from PLINK eigenvectors."""
import argparse
import pandas as pd
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument("--eigenvec", required=True)
p.add_argument("--eigenval", help="Optional PLINK .eigenval file for variance-explained labels")
p.add_argument("--groups", help="TSV with columns sample_id and population")
p.add_argument("--output", default="pca.png")
p.add_argument("--title", default="Principal component analysis")
a = p.parse_args()

x = pd.read_csv(a.eigenvec, sep=r"\s+", header=None, comment="#")
if x.shape[1] < 4:
    raise SystemExit("Expected PLINK eigenvec with at least 4 columns (FID IID PC1 PC2).")
x = x.iloc[:, :4]
x.columns = ["FID", "sample_id", "PC1", "PC2"]

xlabel, ylabel = "PC1", "PC2"
if a.eigenval:
    vals = pd.read_csv(a.eigenval, sep=r"\s+", header=None).iloc[:, 0].astype(float)
    if len(vals) >= 2 and vals.sum() > 0:
        pct = vals / vals.sum() * 100
        xlabel = f"PC1 ({pct.iloc[0]:.1f}%)"
        ylabel = f"PC2 ({pct.iloc[1]:.1f}%)"

if a.groups:
    g = pd.read_csv(a.groups, sep="\t")
    x = x.merge(g[["sample_id", "population"]], on="sample_id", how="left")
else:
    x["population"] = "Samples"

fig, ax = plt.subplots(figsize=(6.6, 5.3))
for pop, d in x.groupby("population", dropna=False):
    ax.scatter(d.PC1, d.PC2, s=38, alpha=0.85, label=str(pop))
ax.axhline(0, linewidth=0.6, alpha=0.35)
ax.axvline(0, linewidth=0.6, alpha=0.35)
ax.set_xlabel(xlabel)
ax.set_ylabel(ylabel)
ax.set_title(a.title)
if x["population"].nunique(dropna=False) > 1:
    ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(a.output, dpi=240, bbox_inches="tight")

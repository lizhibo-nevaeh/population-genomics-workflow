#!/usr/bin/env python3
"""Plot an ADMIXTURE Q matrix as a stacked ancestry barplot."""
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument("--q", required=True, help="ADMIXTURE .Q file")
p.add_argument("--fam", required=True, help="PLINK .fam file corresponding to Q rows")
p.add_argument("--groups", help="Optional TSV with sample_id and population columns")
p.add_argument("--output", default="admixture.png")
p.add_argument("--title", default="ADMIXTURE")
a = p.parse_args()

q = pd.read_csv(a.q, sep=r"\s+", header=None)
fam = pd.read_csv(a.fam, sep=r"\s+", header=None, usecols=[1], names=["sample_id"])
if len(q) != len(fam):
    raise SystemExit("Q and FAM row counts differ.")
d = pd.concat([fam, q], axis=1)

if a.groups:
    g = pd.read_csv(a.groups, sep="\t")
    d = d.merge(g[["sample_id", "population"]], on="sample_id", how="left")
    d["_order"] = pd.Categorical(d["population"]).codes
    d = d.sort_values(["_order", "sample_id"]).reset_index(drop=True)
else:
    d["population"] = "Samples"

qcols = [c for c in d.columns if isinstance(c, int)]
x = np.arange(len(d))
bottom = np.zeros(len(d))
fig, ax = plt.subplots(figsize=(max(7, len(d) * 0.12), 4.2))
for c in qcols:
    vals = d[c].to_numpy(float)
    ax.bar(x, vals, bottom=bottom, width=1.0, linewidth=0)
    bottom += vals
ax.set_xlim(-0.5, len(d)-0.5)
ax.set_ylim(0, 1)
ax.set_ylabel("Ancestry proportion")
ax.set_title(a.title)
ax.set_xticks([])

if a.groups:
    starts = []
    last = None
    for i, pop in enumerate(d["population"].astype(str)):
        if pop != last:
            starts.append((i, pop)); last = pop
    for idx, (start, pop) in enumerate(starts):
        end = starts[idx+1][0] if idx+1 < len(starts) else len(d)
        if start > 0: ax.axvline(start-0.5, lw=0.6)
        ax.text((start+end-1)/2, -0.055, pop, ha="center", va="top", fontsize=8, transform=ax.get_xaxis_transform())
fig.tight_layout()
fig.savefig(a.output, dpi=220, bbox_inches="tight")

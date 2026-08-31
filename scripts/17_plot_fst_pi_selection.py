#!/usr/bin/env python3
"""Joint Fst + nucleotide-diversity-ratio selective-sweep plot."""
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

p = argparse.ArgumentParser()
p.add_argument("--fst", required=True, help="vcftools windowed.weir.fst file")
p.add_argument("--pi-a", required=True, help="vcftools windowed.pi file for population A")
p.add_argument("--pi-b", required=True, help="vcftools windowed.pi file for population B")
p.add_argument("--name-a", default="Population A")
p.add_argument("--name-b", default="Population B")
p.add_argument("--cutoff", type=float, default=0.01, help="Tail fraction used for Fst and pi-ratio thresholds")
p.add_argument("--fst-col", default="WEIGHTED_FST")
p.add_argument("--output", default="fst_pi_selection.png")
p.add_argument("--selected-output", default="fst_pi_selected.tsv")
p.add_argument("--title", default="Joint Fst + nucleotide diversity scan")
a = p.parse_args()

if not 0 < a.cutoff < 0.5:
    raise SystemExit("--cutoff must be between 0 and 0.5")

fst = pd.read_csv(a.fst, sep=r"\s+")
pia = pd.read_csv(a.pi_a, sep=r"\s+")
pib = pd.read_csv(a.pi_b, sep=r"\s+")
keys = ["CHROM", "BIN_START", "BIN_END"]
for d, label in [(fst, "Fst"), (pia, "pi A"), (pib, "pi B")]:
    missing = [k for k in keys if k not in d.columns]
    if missing:
        raise SystemExit(f"{label} file missing columns: {', '.join(missing)}")
if a.fst_col not in fst.columns:
    raise SystemExit(f"Fst column not found: {a.fst_col}")
if "PI" not in pia.columns or "PI" not in pib.columns:
    raise SystemExit("pi files must contain a PI column")

x = fst[keys + [a.fst_col]].merge(
    pia[keys + ["PI"]].rename(columns={"PI": "PI_A"}), on=keys, how="inner"
).merge(
    pib[keys + ["PI"]].rename(columns={"PI": "PI_B"}), on=keys, how="inner"
)
for c in [a.fst_col, "PI_A", "PI_B"]:
    x[c] = pd.to_numeric(x[c], errors="coerce")
x = x.replace([np.inf, -np.inf], np.nan).dropna()
x = x[(x["PI_A"] > 0) & (x["PI_B"] > 0)].copy()
x["log2_pi_ratio"] = np.log2(x["PI_A"] / x["PI_B"])

fst_thr = x[a.fst_col].quantile(1 - a.cutoff)
ratio_low = x["log2_pi_ratio"].quantile(a.cutoff)
ratio_high = x["log2_pi_ratio"].quantile(1 - a.cutoff)

x["category"] = "background"
high_fst = x[a.fst_col] >= fst_thr
x.loc[high_fst, "category"] = "high_Fst"
x.loc[high_fst & (x["log2_pi_ratio"] <= ratio_low), "category"] = f"{a.name_a}_lower_pi"
x.loc[high_fst & (x["log2_pi_ratio"] >= ratio_high), "category"] = f"{a.name_b}_lower_pi"
selected = x[x["category"].isin([f"{a.name_a}_lower_pi", f"{a.name_b}_lower_pi"])].copy()
selected.to_csv(a.selected_output, sep="\t", index=False)

fig = plt.figure(figsize=(8.2, 7.2))
gs = GridSpec(4, 4, figure=fig, hspace=0.06, wspace=0.06)
ax_top = fig.add_subplot(gs[0, :3])
ax_main = fig.add_subplot(gs[1:, :3], sharex=ax_top)
ax_right = fig.add_subplot(gs[1:, 3], sharey=ax_main)

for category, d in x.groupby("category", sort=False):
    if category == "background":
        ax_main.scatter(d["log2_pi_ratio"], d[a.fst_col], s=7, alpha=0.25, label=category)
    else:
        ax_main.scatter(d["log2_pi_ratio"], d[a.fst_col], s=12, alpha=0.85, label=category)

ax_main.axhline(fst_thr, linestyle="--", linewidth=1)
ax_main.axvline(ratio_low, linestyle="--", linewidth=1)
ax_main.axvline(ratio_high, linestyle="--", linewidth=1)
ax_main.set_xlabel(f"log2(pi {a.name_a} / pi {a.name_b})")
ax_main.set_ylabel("Fst")
ax_main.legend(frameon=False, fontsize=8, loc="best")

ax_top.hist(x["log2_pi_ratio"], bins=60, alpha=0.8)
ax_top.axvline(ratio_low, linestyle="--", linewidth=1)
ax_top.axvline(ratio_high, linestyle="--", linewidth=1)
ax_top.set_ylabel("Windows")
ax_top.tick_params(labelbottom=False)

ax_right.hist(x[a.fst_col], bins=60, orientation="horizontal", alpha=0.8)
ax_right.axhline(fst_thr, linestyle="--", linewidth=1)
ax_right.set_xlabel("Windows")
ax_right.tick_params(labelleft=False)

fig.suptitle(a.title)
fig.savefig(a.output, dpi=240, bbox_inches="tight")

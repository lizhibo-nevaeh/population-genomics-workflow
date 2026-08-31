#!/usr/bin/env python3
"""Plot a Newick phylogeny, optionally coloring tip labels by population."""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from Bio import Phylo

p = argparse.ArgumentParser()
p.add_argument("--tree", required=True)
p.add_argument("--groups", help="TSV with sample_id and population columns")
p.add_argument("--output", default="phylogeny.png")
p.add_argument("--title", default="Maximum-likelihood phylogeny")
p.add_argument("--width", type=float, default=8.0)
p.add_argument("--height", type=float, default=8.0)
a = p.parse_args()

tree = Phylo.read(a.tree, "newick")
label_colors = None
legend_handles = []
if a.groups:
    g = pd.read_csv(a.groups, sep="\t")
    sample_to_pop = dict(zip(g["sample_id"].astype(str), g["population"].astype(str)))
    pops = list(dict.fromkeys(g["population"].astype(str)))
    cmap = plt.get_cmap("tab10")
    pop_to_color = {pop: cmap(i % cmap.N) for i, pop in enumerate(pops)}
    label_colors = {tip.name: pop_to_color.get(sample_to_pop.get(str(tip.name), ""), "black") for tip in tree.get_terminals()}
    legend_handles = [Line2D([0], [0], marker="o", linestyle="", color=pop_to_color[p], label=p) for p in pops]

fig, ax = plt.subplots(figsize=(a.width, a.height))
Phylo.draw(tree, axes=ax, do_show=False, label_colors=label_colors, show_confidence=True)
ax.set_title(a.title)
ax.set_xlabel("Branch length")
ax.set_ylabel("")
if legend_handles:
    ax.legend(handles=legend_handles, frameon=False, fontsize=8, loc="best")
fig.tight_layout()
fig.savefig(a.output, dpi=240, bbox_inches="tight")

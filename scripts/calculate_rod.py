#!/usr/bin/env python3
"""Calculate reduction of diversity (ROD) from two vcftools windowed-pi tables.

ROD = 1 - pi_A / pi_B
"""
import argparse
import csv

p = argparse.ArgumentParser()
p.add_argument("--pi-a", required=True)
p.add_argument("--pi-b", required=True)
p.add_argument("--name-a", default="POP_A")
p.add_argument("--name-b", default="POP_B")
p.add_argument("--output", required=True)
a = p.parse_args()

def load(path):
    d = {}
    with open(path, newline="") as fh:
        r = csv.DictReader(fh, delimiter="\t")
        for row in r:
            key = (row["CHROM"], row["BIN_START"], row["BIN_END"])
            try:
                d[key] = float(row["PI"])
            except (ValueError, TypeError):
                continue
    return d

A = load(a.pi_a)
B = load(a.pi_b)
keys = sorted(set(A) & set(B), key=lambda x: (x[0], int(x[1])))

with open(a.output, "w", newline="") as out:
    w = csv.writer(out, delimiter="\t")
    w.writerow(["CHROM", "BIN_START", "BIN_END", f"PI_{a.name_a}", f"PI_{a.name_b}", "ROD"])
    for k in keys:
        pa, pb = A[k], B[k]
        rod = "NA" if pb == 0 else 1.0 - pa / pb
        w.writerow([*k, pa, pb, rod])

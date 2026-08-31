#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"
: "${SELECTED_BED:?Set SELECTED_BED to a BED file of candidate windows/regions}"

OUTDIR="$WORKDIR/12_candidate_regions"
mkdir -p "$OUTDIR"

# Merge overlapping candidate windows.
bedtools sort -i "$SELECTED_BED" | bedtools merge -i - > "$OUTDIR/candidate_regions.merged.bed"

# Extract gene features from GFF/GFF3 and intersect with candidate regions.
awk 'BEGIN{OFS="\t"} $0 !~ /^#/ && $3=="gene" {print $1,$4-1,$5,$9}' "$GFF" \
  > "$OUTDIR/genes.bed"

bedtools intersect -wa -wb \
  -a "$OUTDIR/candidate_regions.merged.bed" \
  -b "$OUTDIR/genes.bed" \
  > "$OUTDIR/candidate_genes.tsv"

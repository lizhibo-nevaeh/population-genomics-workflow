#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

VCF="$WORKDIR/06_filter_variants/cohort.filtered.snps.vcf.gz"
OUTDIR="$WORKDIR/10_diversity_selection"
POPDIR="$OUTDIR/populations"
mkdir -p "$POPDIR"

mapfile -t POPS < <(tail -n +2 "$GROUPS" | awk -F '\t' '{print $2}' | sort -u)

for pop in "${POPS[@]}"; do
  keep="$POPDIR/${pop}.samples.txt"
  awk -F '\t' -v p="$pop" 'NR>1 && $2==p {print $1}' "$GROUPS" > "$keep"

  vcftools --gzvcf "$VCF" --window-pi "$WINDOW" --window-pi-step "$STEP" \
    --keep "$keep" --out "$OUTDIR/pi.${pop}"

  vcftools --gzvcf "$VCF" --TajimaD "$TAJIMA_WINDOW" \
    --keep "$keep" --out "$OUTDIR/tajima.${pop}"
done

# Pairwise Fst and ROD for all population pairs.
for ((i=0; i<${#POPS[@]}; i++)); do
  for ((j=i+1; j<${#POPS[@]}; j++)); do
    A=${POPS[$i]}
    B=${POPS[$j]}

    vcftools --gzvcf "$VCF" \
      --fst-window-size "$WINDOW" --fst-window-step "$STEP" \
      --weir-fst-pop "$POPDIR/${A}.samples.txt" \
      --weir-fst-pop "$POPDIR/${B}.samples.txt" \
      --out "$OUTDIR/Fst.${A}.${B}"

    python3 "$(dirname "$0")/calculate_rod.py" \
      --pi-a "$OUTDIR/pi.${A}.windowed.pi" \
      --pi-b "$OUTDIR/pi.${B}.windowed.pi" \
      --name-a "$A" --name-b "$B" \
      --output "$OUTDIR/ROD.${A}.${B}.tsv"
  done
done

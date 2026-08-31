#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

VCF="$WORKDIR/06_filter_variants/cohort.filtered.snps.vcf.gz"
OUTDIR="$WORKDIR/09_ld_decay"
mkdir -p "$OUTDIR/populations"

# Build one sample list per population from the two-column table.
tail -n +2 "$GROUPS" | awk -F '\t' '{print $2}' | sort -u | while read -r pop; do
  awk -F '\t' -v p="$pop" 'NR>1 && $2==p {print $1}' "$GROUPS" \
    > "$OUTDIR/populations/${pop}.samples.txt"

  PopLDdecay -InVCF "$VCF" \
    -SubPop "$OUTDIR/populations/${pop}.samples.txt" \
    -MaxDist 500 -OutStat "$OUTDIR/${pop}.stat"
done

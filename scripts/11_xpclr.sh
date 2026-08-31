#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

: "${POP_A:?Set POP_A to a population label from the groups file}"
: "${POP_B:?Set POP_B to a population label from the groups file}"

VCF="$WORKDIR/06_filter_variants/cohort.filtered.snps.vcf.gz"
OUTDIR="$WORKDIR/11_xpclr/${POP_A}_vs_${POP_B}"
mkdir -p "$OUTDIR"

A_LIST="$OUTDIR/${POP_A}.samples.txt"
B_LIST="$OUTDIR/${POP_B}.samples.txt"
awk -F '\t' -v p="$POP_A" 'NR>1 && $2==p {print $1}' "$GROUPS" > "$A_LIST"
awk -F '\t' -v p="$POP_B" 'NR>1 && $2==p {print $1}' "$GROUPS" > "$B_LIST"

while read -r chr; do
  [[ -z "$chr" || "$chr" == \#* ]] && continue
  xpclr --format vcf --input "$VCF" \
    --samplesA "$A_LIST" --samplesB "$B_LIST" \
    --out "$OUTDIR/${chr}.xpclr" --chr "$chr" \
    --size "$WINDOW" --step "$STEP" \
    --maxsnps "$XPCLR_MAXSNPS" --minsnps "$XPCLR_MINSNPS"
done < "$CHROMS"

awk 'FNR==1 && NR!=1{next}{print}' "$OUTDIR"/*.xpclr > "$OUTDIR/all_chromosomes.xpclr"

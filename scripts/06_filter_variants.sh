#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

OUTDIR="$WORKDIR/06_filter_variants"
mkdir -p "$OUTDIR"

if [[ -z "${RAW_VCF:-}" ]]; then
  RAW_VCF="$WORKDIR/05_concordant_callset/cohort.concordant.vcf.gz"
fi

VARFILTER="$OUTDIR/cohort.varfilter.vcf.gz"
CLEAN="$OUTDIR/cohort.filtered.snps.vcf.gz"

# Remove SNPs near indels/gaps, then apply site/genotype filters.
vcfutils.pl varFilter -w "$INDEL_WINDOW" -W "$ADJACENT_GAP_WINDOW" \
  "gzip -dc $RAW_VCF|" | gzip -c > "$VARFILTER"

vcftools --gzvcf "$VARFILTER" \
  --recode --recode-INFO-all --stdout \
  --maf "$MAF" \
  --max-missing "$MAX_MISSING" \
  --minDP "$MIN_DP" \
  --maxDP "$MAX_DP" \
  --minQ "$MIN_QUAL" \
  --minGQ "$MIN_GQ" \
  --min-alleles 2 --max-alleles 2 \
  --remove-indels | bgzip -c > "$CLEAN"

tabix -f -p vcf "$CLEAN"
echo "$CLEAN"

#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

VCF="$WORKDIR/06_filter_variants/cohort.filtered.snps.vcf.gz"
OUTDIR="$WORKDIR/07_population_structure"
mkdir -p "$OUTDIR"
cd "$OUTDIR"

# PCA
plink --vcf "$VCF" --pca 10 --out pca \
  --allow-extra-chr --set-missing-var-ids '@:#' --vcf-half-call missing

# LD pruning for ADMIXTURE / structure-like analyses
plink --vcf "$VCF" \
  --indep-pairwise "$LD_WINDOW" "$LD_STEP" "$LD_R2" \
  --out ld --allow-extra-chr --set-missing-var-ids '@:#'

plink --vcf "$VCF" --make-bed --extract ld.prune.in \
  --out admixture --allow-extra-chr --set-missing-var-ids '@:#' \
  --keep-allele-order

for k in $(seq "$ADMIXTURE_K_MIN" "$ADMIXTURE_K_MAX"); do
  admixture -j"$ADMIXTURE_THREADS" --cv admixture.bed "$k" \
    > "admixture.K${k}.log" 2>&1
done

grep -H "CV error" admixture.K*.log || true

#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

GATK_VCF="$WORKDIR/03_joint_genotyping/cohort.raw.vcf.gz"
SAMTOOLS_VCF="$WORKDIR/04_samtools_bcftools_call/cohort.samtools_bcftools.raw.vcf.gz"
OUTDIR="$WORKDIR/05_concordant_callset"
mkdir -p "$OUTDIR"

[[ -f "$GATK_VCF" ]] || { echo "GATK VCF not found: $GATK_VCF" >&2; exit 1; }
[[ -f "$SAMTOOLS_VCF" ]] || { echo "SAMtools/bcftools VCF not found: $SAMTOOLS_VCF" >&2; exit 1; }

GATK_NORM="$OUTDIR/gatk.normalized.vcf.gz"
SAMTOOLS_NORM="$OUTDIR/samtools_bcftools.normalized.vcf.gz"
CONCORDANT="$OUTDIR/cohort.concordant.vcf.gz"

# Normalize multiallelic/indel representation before comparing the callsets.
bcftools norm -f "$REF" -m -any -Oz -o "$GATK_NORM" "$GATK_VCF"
bcftools norm -f "$REF" -m -any -Oz -o "$SAMTOOLS_NORM" "$SAMTOOLS_VCF"
bcftools index -f "$GATK_NORM"
bcftools index -f "$SAMTOOLS_NORM"

# Keep records present in both callsets; output records are taken from the GATK VCF.
bcftools isec -n=2 -w1 -Oz -o "$CONCORDANT" "$GATK_NORM" "$SAMTOOLS_NORM"
bcftools index -f "$CONCORDANT"

echo "$CONCORDANT"

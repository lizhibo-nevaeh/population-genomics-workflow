#!/usr/bin/env bash
set -euo pipefail
CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

GVCFDIR="$WORKDIR/02_gvcf"
OUTDIR="$WORKDIR/03_joint_genotyping"
mkdir -p "$OUTDIR"

combined="$OUTDIR/cohort.combined.g.vcf.gz"
raw="$OUTDIR/cohort.raw.vcf.gz"

variants=()
while IFS= read -r gvcf; do
  variants+=(--variant "$gvcf")
done < <(find "$GVCFDIR" -maxdepth 1 -type f -name '*.g.vcf.gz' | sort)

(( ${#variants[@]} > 0 )) || { echo "No GVCFs found in $GVCFDIR" >&2; exit 1; }

gatk --java-options "-Xmx${GATK_JAVA_MEM}" CombineGVCFs \
  -R "$REF" "${variants[@]}" -O "$combined"

gatk --java-options "-Xmx${GATK_JAVA_MEM}" GenotypeGVCFs \
  -R "$REF" -V "$combined" -O "$raw"

echo "$raw"

#!/usr/bin/env bash
set -euo pipefail
CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

BAMDIR="$WORKDIR/01_alignment"
OUTDIR="$WORKDIR/02_gvcf"
mkdir -p "$OUTDIR"

# Call per-sample germline variants with GATK HaplotypeCaller in GVCF mode.
# Version-specific experimental options from the old notes are intentionally not hard-coded.
tail -n +2 "$SAMPLE_SHEET" | while IFS=$'\t' read -r sample r1 r2 population; do
  [[ -n "$sample" ]] || continue
  bam="$BAMDIR/${sample}.dedup.bam"
  out="$OUTDIR/${sample}.g.vcf.gz"
  [[ -f "$bam" ]] || { echo "BAM not found: $bam" >&2; exit 1; }

  extra=()
  if [[ -n "${GATK_HC_EXTRA_ARGS:-}" ]]; then
    # shellcheck disable=SC2206
    extra=( ${GATK_HC_EXTRA_ARGS} )
  fi

  gatk --java-options "-Xmx${GATK_JAVA_MEM}" HaplotypeCaller \
    -R "$REF" -I "$bam" -O "$out" -ERC GVCF \
    "${extra[@]}"
done

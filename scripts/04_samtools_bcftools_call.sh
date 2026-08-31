#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

BAMDIR="$WORKDIR/01_alignment"
OUTDIR="$WORKDIR/04_samtools_bcftools_call"
mkdir -p "$OUTDIR"

BAMLIST="$OUTDIR/bams.list"
find "$BAMDIR" -maxdepth 1 -type f -name '*.dedup.bam' | sort > "$BAMLIST"
[[ -s "$BAMLIST" ]] || { echo "No BAMs found in $BAMDIR" >&2; exit 1; }

RAW="$OUTDIR/cohort.samtools_bcftools.raw.vcf.gz"

# Run an independent SAMtools/bcftools-style multi-sample calling route.
# For portability, this implementation uses the
# current bcftools mpileup/call interface for the same multi-sample concept.
bcftools mpileup \
  --threads "$BCFTOOLS_THREADS" \
  -Ou -f "$REF" -b "$BAMLIST" | \
  bcftools call --threads "$BCFTOOLS_THREADS" -mv -Oz -o "$RAW"

bcftools index -f "$RAW"
echo "$RAW"

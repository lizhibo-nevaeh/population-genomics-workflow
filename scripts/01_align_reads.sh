#!/usr/bin/env bash
set -euo pipefail
CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

OUTDIR="$WORKDIR/01_alignment"
TMPDIR="$OUTDIR/tmp"
mkdir -p "$OUTDIR" "$TMPDIR"

[[ -f "$SAMPLE_SHEET" ]] || { echo "Sample sheet not found: $SAMPLE_SHEET" >&2; exit 1; }

# Align paired-end reads with BWA-MEM, then sort and mark duplicate reads.
tail -n +2 "$SAMPLE_SHEET" | while IFS=$'\t' read -r sample r1 r2 population; do
  [[ -n "$sample" ]] || continue
  [[ -f "$r1" && -f "$r2" ]] || { echo "FASTQ missing for $sample" >&2; exit 1; }

  name_bam="$TMPDIR/${sample}.name.bam"
  fix_bam="$TMPDIR/${sample}.fixmate.bam"
  pos_bam="$TMPDIR/${sample}.pos.bam"
  out_bam="$OUTDIR/${sample}.dedup.bam"

  bwa mem -t "$BWA_THREADS" \
    -R "@RG\tID:${sample}\tLB:${sample}\tPL:ILLUMINA\tSM:${sample}" \
    "$REF" "$r1" "$r2" | \
    samtools sort -n -@ "$SAMTOOLS_THREADS" -o "$name_bam" -

  samtools fixmate -m "$name_bam" "$fix_bam"
  samtools sort -@ "$SAMTOOLS_THREADS" -o "$pos_bam" "$fix_bam"
  samtools markdup -r -@ "$SAMTOOLS_THREADS" "$pos_bam" "$out_bam"
  samtools index "$out_bam"

  rm -f "$name_bam" "$fix_bam" "$pos_bam"
  echo "$sample -> $out_bam"
done

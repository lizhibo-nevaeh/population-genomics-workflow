#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"
: "${BAM:?Set BAM=/path/to/sample.bam}"
: "${SAMPLE:?Set SAMPLE=sample_name}"

OUTDIR="$WORKDIR/13_psmc/$SAMPLE"
mkdir -p "$OUTDIR"

CONSENSUS_FQ="$OUTDIR/${SAMPLE}.psmc.fq.gz"
PSMC_FA="$OUTDIR/${SAMPLE}.psmc.fa"
PSMC_OUT="$OUTDIR/${SAMPLE}.psmc"
SPLIT_FA="$OUTDIR/${SAMPLE}.split.psmcfa"

bcftools mpileup -Ou -I -f "$REF" "$BAM" | \
  bcftools call -c -Ov | \
  vcfutils.pl vcf2fq -d "$PSMC_MIN_DEPTH" -D "$PSMC_MAX_DEPTH" | \
  gzip -c > "$CONSENSUS_FQ"

fq2psmcfa -q20 "$CONSENSUS_FQ" > "$PSMC_FA"

psmc -N"$PSMC_N" -t"$PSMC_T" -r"$PSMC_R" -p "$PSMC_PATTERN" \
  -o "$PSMC_OUT" "$PSMC_FA"

# Bootstrap replicates.
splitfa "$PSMC_FA" 100000 > "$SPLIT_FA"
for i in $(seq 1 "$PSMC_BOOTSTRAPS"); do
  psmc -N"$PSMC_N" -t"$PSMC_T" -r"$PSMC_R" -b -p "$PSMC_PATTERN" \
    -o "$OUTDIR/${SAMPLE}.bootstrap.${i}.psmc" "$SPLIT_FA"
done

cat "$PSMC_OUT" "$OUTDIR"/${SAMPLE}.bootstrap.*.psmc \
  > "$OUTDIR/${SAMPLE}.combined.psmc"

# Plot the combined estimate and bootstrap curves with scripts/20_plot_psmc.py.

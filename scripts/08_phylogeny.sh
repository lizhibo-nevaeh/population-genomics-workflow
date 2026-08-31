#!/usr/bin/env bash
set -euo pipefail

CFG=${1:?"Usage: $0 config.sh"}
# shellcheck source=/dev/null
source "$CFG"

VCF="$WORKDIR/06_filter_variants/cohort.filtered.snps.vcf.gz"
OUTDIR="$WORKDIR/08_phylogeny"
mkdir -p "$OUTDIR"
cd "$OUTDIR"

# Convert VCF to interleaved PHYLIP with TASSEL.
run_pipeline.pl -Xmx20G -importGuess "$VCF" \
  -ExportPlugin -saveAs cohort.phy -format Phylip_Inter

# Maximum-likelihood phylogeny.
iqtree2 -s cohort.phy -st DNA -T AUTO -m GTR -B 1000 -bnni \
  --prefix cohort_iqtree

# A fast approximate tree can optionally be generated with:
# FastTree -nt -gtr cohort.phy > cohort.fasttree.nwk
